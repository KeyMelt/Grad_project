from __future__ import annotations

from typing import Any

from backend.services.firebase_progress_service import FirebaseProgressService
from backend.services.quiz_service import QuizService


class UserEvaluationService:
    """Composite service for auth, dashboard, quiz lifecycle, and N-gain metrics."""

    def __init__(
        self,
        *,
        progress_service: FirebaseProgressService,
        quiz_service: QuizService | None = None,
    ) -> None:
        self._progress_service = progress_service
        self._quiz_service = quiz_service or QuizService(progress_service)

    def sign_in(
        self,
        display_name: str,
        password: str,
        firebase_id_token: str | None = None,
    ) -> dict[str, Any]:
        return self._progress_service.sign_in(display_name, password, firebase_id_token)

    def get_dashboard(self, student_id: str) -> dict[str, Any] | None:
        return self._progress_service.get_dashboard(student_id)

    def start_quiz(self, student_id: str, phase: str) -> dict[str, Any]:
        return self._quiz_service.start_session(student_id=student_id, phase=phase)

    def submit_quiz(
        self,
        student_id: str,
        session_id: str,
        answers: list[dict[str, int]],
    ) -> dict[str, Any]:
        return self._quiz_service.submit_session(
            student_id=student_id,
            session_id=session_id,
            answers=answers,
        )

    def list_n_gain_metrics(self) -> list[dict[str, Any]]:
        return self._progress_service.list_n_gain_metrics()

    def close(self) -> None:
        self._progress_service.close()

    @property
    def progress_service(self) -> FirebaseProgressService:
        return self._progress_service
