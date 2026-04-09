from datetime import datetime, timezone
import hashlib
import hmac
import json
import secrets
from threading import Lock
from typing import Optional
from uuid import uuid4

from sqlmodel import select

from backend.models.student_progress_record import StudentProgressRecord
from backend.persistence import Database


class StudentProgressService:
    """Stores learner sign-in state and progress in a SQL database."""

    def __init__(
        self,
        *,
        database: Optional[Database] = None,
        database_url: Optional[str] = None,
    ) -> None:
        self._lock = Lock()
        self._database = database or Database(database_url)
        self._database.create_schema()
        self._ensure_password_columns()

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: Optional[str] = None,
    ) -> dict:
        del firebase_id_token
        normalized_name = " ".join(display_name.split())
        if not normalized_name:
            raise ValueError("Display name cannot be empty.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        lookup_key = normalized_name.casefold()
        with self._lock:
            with self._database.session() as session:
                record = session.exec(
                    select(StudentProgressRecord).where(
                        StudentProgressRecord.normalized_name == lookup_key
                    )
                ).first()

                if record is None:
                    password_salt, password_hash = self._hash_password(password)
                    record = StudentProgressRecord(
                        id=uuid4().hex,
                        display_name=normalized_name,
                        normalized_name=lookup_key,
                        password_salt=password_salt,
                        password_hash=password_hash,
                    )
                    session.add(record)
                    session.commit()
                    session.refresh(record)
                else:
                    if (
                        not record.password_hash
                        or not record.password_salt
                    ):
                        # Upgrade legacy account rows that predate password auth.
                        password_salt, password_hash = self._hash_password(password)
                        record.password_salt = password_salt
                        record.password_hash = password_hash
                        record.updated_at = datetime.now(timezone.utc)
                        session.add(record)
                        session.commit()
                        session.refresh(record)
                    elif not self._verify_password(
                        password=password,
                        stored_salt=record.password_salt,
                        stored_hash=record.password_hash,
                    ):
                        raise ValueError("Invalid display name or password.")

                return self._dashboard_payload(record)

    def get_dashboard(self, student_id: str) -> Optional[dict]:
        with self._lock:
            record = self._get_record(student_id)
            if record is None:
                return None
            return self._dashboard_payload(record)

    def record_lesson_completion(
        self,
        student_id: str,
        lesson_id: str,
    ) -> Optional[dict]:
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudentProgressRecord, student_id)
                if record is None:
                    return None

                completed_lesson_ids = self._decode_list(
                    record.completed_lesson_ids_json
                )
                if lesson_id not in completed_lesson_ids:
                    completed_lesson_ids.append(lesson_id)

                record.completed_lesson_ids_json = self._encode_list(
                    completed_lesson_ids
                )
                record.successful_runs += 1
                record.latest_lesson_id = lesson_id
                record.updated_at = datetime.now(timezone.utc)
                session.add(record)
                session.commit()
                session.refresh(record)
                return self._dashboard_payload(record)

    def record_quiz_result(
        self,
        student_id: str,
        phase: str,
        percentage: float,
        question_ids: list[str],
    ) -> Optional[dict]:
        with self._lock:
            with self._database.session() as session:
                record = session.get(StudentProgressRecord, student_id)
                if record is None:
                    return None

                if phase not in {"pretest", "posttest"}:
                    raise ValueError(f"Unsupported quiz phase '{phase}'.")

                if phase == "pretest":
                    record.quiz_attempts_pretest += 1
                    record.pretest_score = percentage
                else:
                    record.quiz_attempts_posttest += 1
                    record.posttest_score = percentage

                question_history = self._decode_list(record.question_history_json)
                question_history.extend(question_ids)
                record.question_history_json = self._encode_list(question_history)
                record.n_gain = self._compute_n_gain(
                    record.pretest_score,
                    record.posttest_score,
                )
                record.updated_at = datetime.now(timezone.utc)
                session.add(record)
                session.commit()
                session.refresh(record)
                return self._dashboard_payload(record)

    def get_question_history(self, student_id: str) -> list[str]:
        with self._lock:
            record = self._get_record(student_id)
            if record is None:
                return []
            return self._decode_list(record.question_history_json)

    def list_n_gain_metrics(self) -> list[dict]:
        with self._lock:
            with self._database.session() as session:
                records = session.exec(
                    select(StudentProgressRecord).order_by(
                        StudentProgressRecord.display_name
                    )
                ).all()

                rows: list[dict] = []
                for record in records:
                    completed_ids = self._decode_list(record.completed_lesson_ids_json)
                    rows.append(
                        {
                            "student_id": record.id,
                            "display_name": record.display_name,
                            "pretest_score": record.pretest_score,
                            "posttest_score": record.posttest_score,
                            "n_gain": record.n_gain,
                            "successful_runs": record.successful_runs,
                            "lessons_completed": len(completed_ids),
                            "quiz_attempts_pretest": record.quiz_attempts_pretest,
                            "quiz_attempts_posttest": record.quiz_attempts_posttest,
                            "last_updated_utc": record.updated_at.isoformat(),
                        }
                    )
                return rows

    def close(self) -> None:
        self._database.close()

    def _dashboard_payload(self, record: StudentProgressRecord) -> dict:
        completed_lesson_ids = self._decode_list(record.completed_lesson_ids_json)
        return {
            "student": {
                "id": record.id,
                "display_name": record.display_name,
            },
            "progress": {
                "completed_lesson_ids": sorted(completed_lesson_ids),
                "successful_runs": record.successful_runs,
                "latest_lesson_id": record.latest_lesson_id,
                "pretest_score": record.pretest_score,
                "posttest_score": record.posttest_score,
                "n_gain": record.n_gain,
                "quiz_attempts": {
                    "pretest": record.quiz_attempts_pretest,
                    "posttest": record.quiz_attempts_posttest,
                },
            },
        }

    def _get_record(self, student_id: str) -> Optional[StudentProgressRecord]:
        with self._database.session() as session:
            record = session.get(StudentProgressRecord, student_id)
            if record is None:
                return None
            session.expunge(record)
            return record

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

    def _decode_list(self, raw_value: str) -> list[str]:
        try:
            decoded = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
        if not isinstance(decoded, list):
            return []
        return [str(item) for item in decoded]

    def _encode_list(self, values: list[str]) -> str:
        return json.dumps(values)

    def _hash_password(self, password: str) -> tuple[str, str]:
        salt = secrets.token_bytes(16)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            310_000,
        )
        return salt.hex(), derived_key.hex()

    def _verify_password(
        self,
        *,
        password: str,
        stored_salt: str,
        stored_hash: str,
    ) -> bool:
        try:
            salt_bytes = bytes.fromhex(stored_salt)
            expected_bytes = bytes.fromhex(stored_hash)
        except ValueError:
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            310_000,
        )
        return hmac.compare_digest(candidate, expected_bytes)

    def _ensure_password_columns(self) -> None:
        if not self._database.database_url.startswith("sqlite"):
            return

        with self._database.session() as session:
            connection = session.connection()
            column_rows = connection.exec_driver_sql(
                "PRAGMA table_info(student_progress)"
            ).fetchall()
            existing_columns = {row[1] for row in column_rows}
            if "password_hash" not in existing_columns:
                connection.exec_driver_sql(
                    "ALTER TABLE student_progress "
                    "ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''"
                )
            if "password_salt" not in existing_columns:
                connection.exec_driver_sql(
                    "ALTER TABLE student_progress "
                    "ADD COLUMN password_salt TEXT NOT NULL DEFAULT ''"
                )
            session.commit()
