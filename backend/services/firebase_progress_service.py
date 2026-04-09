from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

try:  # pragma: no cover - import availability depends on environment
    import firebase_admin
    from firebase_admin import auth, credentials, firestore
except Exception:  # pragma: no cover
    firebase_admin = None
    auth = None
    credentials = None
    firestore = None


class FirebaseProgressService:
    """
    Firebase-backed learner auth + progress service.

    Expects clients to provide a Firebase ID token via `firebase_id_token` in sign-in.
    """

    def __init__(
        self,
        *,
        credentials_path: Optional[str] = None,
        app_name: str = "rl-ide-backend",
    ) -> None:
        if firebase_admin is None or auth is None or firestore is None:
            raise RuntimeError(
                "firebase-admin is not installed. Add dependency and configure credentials."
            )

        app = self._get_or_create_app(credentials_path=credentials_path, app_name=app_name)
        self._db = firestore.client(app=app)
        self._users = self._db.collection("users")

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if not firebase_id_token:
            raise ValueError(
                "Firebase sign-in requires firebase_id_token. Legacy password flow is disabled."
            )

        decoded = auth.verify_id_token(firebase_id_token)
        uid = decoded.get("uid")
        if not uid:
            raise ValueError("Invalid Firebase token.")

        profile_name = (
            decoded.get("name")
            or decoded.get("email")
            or " ".join(display_name.split())
            or "Student"
        )
        return self._upsert_and_dashboard(uid=uid, display_name=profile_name)

    def get_dashboard(self, student_id: str) -> Optional[dict[str, Any]]:
        snapshot = self._users.document(student_id).get()
        if not snapshot.exists:
            return None
        return self._dashboard_payload(snapshot.id, snapshot.to_dict() or {})

    def record_lesson_completion(
        self,
        student_id: str,
        lesson_id: str,
    ) -> Optional[dict[str, Any]]:
        user_ref = self._users.document(student_id)
        snapshot = user_ref.get()
        if not snapshot.exists:
            return None

        payload = snapshot.to_dict() or {}
        progress = payload.get("progress", {})
        completed_ids = list(progress.get("completed_lesson_ids", []))
        if lesson_id not in completed_ids:
            completed_ids.append(lesson_id)

        progress["completed_lesson_ids"] = sorted(completed_ids)
        progress["successful_runs"] = int(progress.get("successful_runs", 0)) + 1
        progress["latest_lesson_id"] = lesson_id
        payload["progress"] = progress
        payload["updated_at_utc"] = datetime.now(timezone.utc).isoformat()

        user_ref.set(payload)
        return self._dashboard_payload(student_id, payload)

    def record_quiz_result(
        self,
        student_id: str,
        phase: str,
        percentage: float,
        question_ids: list[str],
    ) -> Optional[dict[str, Any]]:
        if phase not in {"pretest", "posttest"}:
            raise ValueError(f"Unsupported quiz phase '{phase}'.")

        user_ref = self._users.document(student_id)
        snapshot = user_ref.get()
        if not snapshot.exists:
            return None

        payload = snapshot.to_dict() or {}
        progress = payload.get("progress", {})
        attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
        attempts[phase] = int(attempts.get(phase, 0)) + 1
        progress["quiz_attempts"] = attempts

        if phase == "pretest":
            progress["pretest_score"] = percentage
        else:
            progress["posttest_score"] = percentage

        question_history = list(progress.get("question_history", []))
        question_history.extend(question_ids)
        progress["question_history"] = question_history
        progress["n_gain"] = self._compute_n_gain(
            progress.get("pretest_score"),
            progress.get("posttest_score"),
        )

        payload["progress"] = progress
        payload["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        user_ref.set(payload)
        return self._dashboard_payload(student_id, payload)

    def get_question_history(self, student_id: str) -> list[str]:
        snapshot = self._users.document(student_id).get()
        if not snapshot.exists:
            return []
        payload = snapshot.to_dict() or {}
        progress = payload.get("progress", {})
        return [str(item) for item in progress.get("question_history", [])]

    def list_n_gain_metrics(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for snapshot in self._users.stream():
            payload = snapshot.to_dict() or {}
            progress = payload.get("progress", {})
            completed_ids = list(progress.get("completed_lesson_ids", []))
            attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
            rows.append(
                {
                    "student_id": snapshot.id,
                    "display_name": payload.get("display_name", "Student"),
                    "pretest_score": progress.get("pretest_score"),
                    "posttest_score": progress.get("posttest_score"),
                    "n_gain": progress.get("n_gain"),
                    "successful_runs": int(progress.get("successful_runs", 0)),
                    "lessons_completed": len(completed_ids),
                    "quiz_attempts_pretest": int(attempts.get("pretest", 0)),
                    "quiz_attempts_posttest": int(attempts.get("posttest", 0)),
                    "last_updated_utc": payload.get("updated_at_utc"),
                }
            )

        rows.sort(key=lambda item: (item.get("display_name") or "").lower())
        return rows

    def close(self) -> None:
        return None

    def _upsert_and_dashboard(self, *, uid: str, display_name: str) -> dict[str, Any]:
        user_ref = self._users.document(uid)
        snapshot = user_ref.get()
        if snapshot.exists:
            payload = snapshot.to_dict() or {}
        else:
            payload = {}

        payload.setdefault("display_name", display_name)
        payload.setdefault(
            "progress",
            {
                "completed_lesson_ids": [],
                "successful_runs": 0,
                "latest_lesson_id": None,
                "pretest_score": None,
                "posttest_score": None,
                "n_gain": None,
                "quiz_attempts": {
                    "pretest": 0,
                    "posttest": 0,
                },
                "question_history": [],
            },
        )
        payload["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        user_ref.set(payload)
        return self._dashboard_payload(uid, payload)

    def _dashboard_payload(self, student_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        progress = payload.get("progress", {})
        attempts = progress.get("quiz_attempts", {"pretest": 0, "posttest": 0})
        return {
            "student": {
                "id": student_id,
                "display_name": payload.get("display_name", "Student"),
            },
            "progress": {
                "completed_lesson_ids": sorted(
                    [str(item) for item in progress.get("completed_lesson_ids", [])]
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
            },
        }

    def _compute_n_gain(
        self,
        pretest_score: Optional[float],
        posttest_score: Optional[float],
    ) -> Optional[float]:
        if pretest_score is None or posttest_score is None:
            return None
        if pretest_score >= 100:
            return 1.0 if posttest_score >= 100 else 0.0
        return round((posttest_score - pretest_score) / (100 - pretest_score), 3)

    def _get_or_create_app(
        self,
        *,
        credentials_path: Optional[str],
        app_name: str,
    ) -> Any:
        try:
            return firebase_admin.get_app(app_name)
        except ValueError:
            pass

        cred = credentials.Certificate(credentials_path) if credentials_path else None
        if cred is None:
            return firebase_admin.initialize_app(name=app_name)
        return firebase_admin.initialize_app(credential=cred, name=app_name)
