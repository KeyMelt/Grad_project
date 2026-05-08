from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api_gateway.schemas import QuizStartRequest, QuizSubmissionRequest


def build_quiz_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.post("/quiz/start")
    def start_quiz(request: QuizStartRequest):
        try:
            return services.user_evaluation.start_quiz(
                student_id=request.student_id,
                phase=request.phase,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @router.post("/quiz/submit")
    def submit_quiz(request: QuizSubmissionRequest):
        try:
            return services.user_evaluation.submit_quiz(
                student_id=request.student_id,
                session_id=request.session_id,
                answers=[answer.model_dump() for answer in request.answers],
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return router
