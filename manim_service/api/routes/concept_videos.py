"""`POST /render/concept-video` — enqueue a concept video render."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from manim_service.jobs.queue import JobKind, get_queue
from manim_service.jobs.worker import CONCEPT_VIDEO_SCENES, KNOWN_LESSON_IDS

router = APIRouter()


class ConceptVideoRequest(BaseModel):
    lesson_id: str = Field(..., description="Canonical lesson id (e.g. dp_value_iteration)")
    force: bool = Field(False, description="Re-render even if the output already exists")


class JobAccepted(BaseModel):
    job_id: str
    status: str


@router.post("/render/concept-video", response_model=JobAccepted, status_code=202)
def enqueue_concept_video(request: ConceptVideoRequest) -> JobAccepted:
    if request.lesson_id not in KNOWN_LESSON_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown lesson_id={request.lesson_id!r}; "
                   f"expected one of {sorted(KNOWN_LESSON_IDS)}",
        )
    if request.lesson_id not in CONCEPT_VIDEO_SCENES:
        raise HTTPException(
            status_code=404,
            detail=f"No concept-video scene registered yet for lesson_id={request.lesson_id!r}",
        )
    job_id = get_queue().enqueue(
        JobKind.CONCEPT_VIDEO,
        {"lesson_id": request.lesson_id, "force": request.force},
    )
    return JobAccepted(job_id=job_id, status="queued")
