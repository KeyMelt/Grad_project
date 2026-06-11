from __future__ import annotations

from typing import Any

from fastapi import APIRouter


def build_flashcards_router(services: Any) -> APIRouter:
    router = APIRouter()

    @router.get("/flashcards")
    def get_flashcards():
        return {"flashcards": services.flashcards.list_flashcards()}

    return router
