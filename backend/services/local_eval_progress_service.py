"""
LocalEvalProgressService
========================
A drop-in replacement for FirebaseProgressService that uses a local SQLite
database instead of Firestore/Firebase.

Activation: set RL_IDE_ALLOW_LOCAL_PASSWORD_AUTH=1 in the environment of the
user-evaluation-service container. Intended ONLY for the AI-agent evaluation
harness - never for production.

Authentication: any (display_name, password) pair is accepted where the
password matches the RL_IDE_AGENT_EVAL_PASSWORD environment variable. If that
variable is absent the service falls back to RL_IDE_AGENT_PASSWORD.

Student IDs are deterministic: SHA-256(display_name.casefold())[:32], so the
same display name always maps to the same student record regardless of how many
times the harness runs.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Optional


_DEFAULT_PROGRESS: dict[str, Any] = {
    "completed_lesson_ids": [],
    "successful_runs": 0,
    "latest_lesson_id": None,
    "pretest_score": None,
    "posttest_score": None,
    "n_gain": None,
    "quiz_attempts": {"pretest": 0, "posttest": 0},
    "question_history": [],
    "total_submission_attempts": 0,
    "passed_submission_attempts": 0,
    "validation_failures": 0,
    "runtime_failures": 0,
    "test_failures": 0,
}

_DB_PATH = os.environ.get(
    "RL_IDE_LOCAL_EVAL_DB",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "eval_local_progress.db",
    ),
)


def _student_id_for(display_name: str) -> str:
    return hashlib.sha256(display_name.strip().casefold().encode()).hexdigest()[:32]


class LocalEvalProgressService:
    """SQLite-backed learner progress service for evaluation use only."""

    def __init__(self, db_path: str = _DB_PATH) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._eval_password = (
            os.environ.get("RL_IDE_AGENT_EVAL_PASSWORD")
            or os.environ.get("RL_IDE_AGENT_PASSWORD")
            or ""
        )
        self._init_db()

    # ------------------------------------------------------------------
    # Public interface (matches FirebaseProgressService)
    # ------------------------------------------------------------------

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if not self._eval_password:
            raise ValueError(
                "RL_IDE_AGENT_EVAL_PASSWORD is not set. "
                "Cannot authenticate evaluation accounts."
            )
        if password != self._eval_password:
            raise ValueError("Invalid display name or password.")

        student_id = _student_id_for(display_name)
        normalized_name = " ".join(display_name.split()) or "Student"
        return self._upsert_and_dashboard(
            student_id=student_id, display_name=normalized_name
        )

    def get_dashboard(self, student_id: str) -> Optional[dict[str, Any]]:
        row = self._fetch(student_id)
        if row is None:
            return None
        return self._dashboard_payload(student_id, row)

    def record_lesson_completion(
        self, student_id: str, lesson_id: str
    ) -> Optional[dict[str, Any]]:
        with self._lock:
            row = self._fetch(student_id)
            if row is None:
                return None
            progress = row["progress"]
            ids = list(progress.get("completed_lesson_ids", []))
            if lesson_id not in ids:
                ids.append(lesson_id)
            progress["completed_lesson_ids"] = sorted(ids)
            progress["successful_runs"] = int(progress.get("successful_runs", 0)) + 1
            progress["latest_lesson_id"] = lesson_id
            row["progress"] = progress
            self._save(student_id, row)
        return self._dashboard_payload(student_id, row)

    def record_submission_outcome(
        self,
        student_id: str,
        *,
        passed: bool,
        failure_kind: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        with self._lock:
            row = self._fetch(student_id)
            if row is None:
                return None
            progress = row["progress"]
            progress["total_submission_attempts"] = (
                int(progress.get("total_submission_attempts", 0)) + 1
            )
            if passed:
                progress["passed_submission_attempts"] = (
                    int(progress.get("passed_submission_attempts", 0)) + 1
                )
            elif failure_kind == "validation_error":
                progress["validation_failures"] = int(progress.get("validation_failures", 0)) + 1
            elif failure_kind == "runtime_error":
                progress["runtime_failures"] = int(progress.get("runtime_failures", 0)) + 1
            elif failure_kind in {"test_failure", "incomplete_template"}:
                progress["test_failures"] = int(progress.get("test_failures", 0)) + 1
            row["progress"] = progress
            self._save(student_id, row)
        return self._dashboard_payload(student_id, row)

    def record_quiz_result(
        self,
        student_id: str,
        phase: str,
        percentage: float,
        question_ids: list[str],
    ) -> Optional[dict[str, Any]]:
        if phase not in {"pretest", "posttest"}:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")
        with self._lock:
            row = self._fetch(student_id)
            if row is None:
                return None
            progress = row["progress"]
            attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
            attempts[phase] = int(attempts.get(phase, 0)) + 1
            progress["quiz_attempts"] = attempts

            history = list(progress.get("question_history", []))
            for qid in question_ids:
                if qid not in history:
                    history.append(qid)
            progress["question_history"] = history

            if phase == "pretest":
                progress["pretest_score"] = percentage
            else:
                progress["posttest_score"] = percentage
                progress["n_gain"] = self._compute_n_gain(
                    progress.get("pretest_score"),
                    progress.get("posttest_score"),
                )
            row["progress"] = progress
            self._save(student_id, row)
        return self._dashboard_payload(student_id, row)

    def get_question_history(self, student_id: str) -> list[str]:
        row = self._fetch(student_id)
        if row is None:
            return []
        return [str(q) for q in row["progress"].get("question_history", [])]

    def list_n_gain_metrics(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT student_id, payload FROM students ORDER BY display_name"
            ).fetchall()
        result = []
        for student_id, payload_json in rows:
            payload = json.loads(payload_json)
            progress = payload.get("progress", {})
            attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
            result.append({
                "student_id": student_id,
                "display_name": payload.get("display_name", "Student"),
                "pretest_score": progress.get("pretest_score"),
                "posttest_score": progress.get("posttest_score"),
                "n_gain": progress.get("n_gain"),
                "successful_runs": int(progress.get("successful_runs", 0)),
                "lessons_completed": len(progress.get("completed_lesson_ids", [])),
                "quiz_attempts_pretest": int(attempts.get("pretest", 0)),
                "quiz_attempts_posttest": int(attempts.get("posttest", 0)),
                "last_updated_utc": payload.get("updated_at_utc"),
            })
        result.sort(key=lambda r: (r.get("display_name") or "").lower())
        return result

    def ensure_student_record(
        self, *, student_id: str, display_name: str
    ) -> dict[str, Any]:
        normalized = " ".join((display_name or "").split()) or "Student"
        with self._lock:
            row = self._fetch(student_id)
            if row is None:
                row = {"display_name": normalized, "progress": dict(_DEFAULT_PROGRESS)}
            elif row.get("display_name") != normalized:
                row["display_name"] = normalized
            row["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
            self._save(student_id, row)
        return self._dashboard_payload(student_id, row)

    def close(self) -> None:
        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT
                )
                """
            )
            conn.commit()

    def _fetch(self, student_id: str) -> Optional[dict[str, Any]]:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def _save(self, student_id: str, payload: dict[str, Any]) -> None:
        payload["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO students (student_id, display_name, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    student_id,
                    payload.get("display_name", "Student"),
                    json.dumps(payload),
                    payload["updated_at_utc"],
                ),
            )
            conn.commit()

    def _upsert_and_dashboard(
        self, *, student_id: str, display_name: str
    ) -> dict[str, Any]:
        with self._lock:
            row = self._fetch(student_id) or {}
            row.setdefault("display_name", display_name)
            row.setdefault("progress", dict(_DEFAULT_PROGRESS))
            row["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
            self._save(student_id, row)
        return self._dashboard_payload(student_id, row)

    def _dashboard_payload(
        self, student_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        progress = payload.get("progress", {})
        attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
        return {
            "student": {
                "id": student_id,
                "display_name": payload.get("display_name", "Student"),
            },
            "progress": {
                "completed_lesson_ids": sorted(
                    [str(i) for i in progress.get("completed_lesson_ids", [])]
                ),
                "successful_runs": int(progress.get("successful_runs", 0)),
                "latest_lesson_id": progress.get("latest_lesson_id"),
                "pretest_score": progress.get("pretest_score"),
                "posttest_score": progress.get("posttest_score"),
                "n_gain": progress.get("n_gain"),
                "quiz_attempts": {
                    "pretest": int(attempts.get("pretest", 0)),
                    "posttest": int(attempts.get("posttest", 0)),
                },
                "total_submission_attempts": int(
                    progress.get("total_submission_attempts", 0)
                ),
                "passed_submission_attempts": int(
                    progress.get("passed_submission_attempts", 0)
                ),
                "validation_failures": int(progress.get("validation_failures", 0)),
                "runtime_failures": int(progress.get("runtime_failures", 0)),
                "test_failures": int(progress.get("test_failures", 0)),
            },
        }

    @staticmethod
    def _compute_n_gain(
        pretest_score: Optional[float],
        posttest_score: Optional[float],
    ) -> Optional[float]:
        if pretest_score is None or posttest_score is None:
            return None
        if pretest_score >= 100:
            return 1.0 if posttest_score >= 100 else 0.0
        return round(
            (posttest_score - pretest_score) / (100 - pretest_score), 3
        )
