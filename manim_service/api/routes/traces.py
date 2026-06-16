"""Trace + job-status + video-serving endpoints.

- `POST /render/trace`     — enqueue an episode-trace render
- `GET  /jobs/{job_id}`    — poll job status (works for both kinds)
- `GET  /videos/{filename}` — serve a rendered MP4 from shared media
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field

from manim_service.jobs.queue import JobKind, JobStatus, get_queue
from manim_service.jobs.worker import KNOWN_LESSON_IDS
from manim_service.storage import output as storage

router = APIRouter()


class TraceStep(BaseModel):
    # `state` is `int` for grid environments but a JSON array `[player_sum,
    # dealer_card, usable_ace]` for Blackjack (tuple states serialised by the
    # backend controller). Accept all three forms so Blackjack MC traces are
    # not rejected with a 422 that silences the replay_render_job_id.
    state: int | list | str
    action: int
    reward: float
    next_state: int | list | str
    done: bool = False
    frame_path: str | None = None
    transition_probability: float | None = None
    agent_caption: str | None = None
    code_title: str | None = None
    code_lines: list[str] | None = None
    math_title: str | None = None
    math_equation: str | None = None
    math_lines: list[str] | None = None
    updated_values: dict[str, Any] | None = None
    equation_update: dict[str, Any] | None = None

    model_config = ConfigDict(extra="allow")


class EpisodeTrace(BaseModel):
    steps: list[TraceStep]
    q_table: dict[str, Any] | None = None


class ReplayEpisodeTrace(BaseModel):
    episode_index: int
    role: str = "episode"
    steps: list[TraceStep]


class TraceRequest(BaseModel):
    lesson_id: str = Field(..., description="Canonical lesson id (e.g. td_q_learning)")
    episode_trace: EpisodeTrace
    episodes: list[ReplayEpisodeTrace] | None = None


class JobAccepted(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    video_url: str | None = None
    error: str | None = None


@router.post("/render/trace", response_model=JobAccepted, status_code=202)
def enqueue_trace(request: TraceRequest) -> JobAccepted:
    if request.lesson_id not in KNOWN_LESSON_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown lesson_id={request.lesson_id!r}; "
                   f"expected one of {sorted(KNOWN_LESSON_IDS)}",
        )
    job_id = get_queue().enqueue(
        JobKind.TRACE,
        {
            "lesson_id": request.lesson_id,
            "episode_trace": request.episode_trace.model_dump(),
            "episodes": (
                [episode.model_dump() for episode in request.episodes]
                if request.episodes is not None
                else None
            ),
        },
    )
    return JobAccepted(job_id=job_id, status="queued")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    job = get_queue().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"job_id={job_id!r} not found")
    video_url: str | None = None
    if job.status == JobStatus.COMPLETE and job.video_path:
        video_path = Path(job.video_path)
        video_url = storage.public_url_for_media_path(video_path)
        if video_url is None:
            video_url = f"/videos/{video_path.name}"
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        video_url=video_url,
        error=job.error,
    )


@router.get("/videos/{filename}")
def get_video(filename: str):
    resolved = storage.resolve_safe_video_path(filename)
    if resolved is None:
        raise HTTPException(status_code=404, detail=f"video {filename!r} not found")
    cdn_url = storage.public_url_for_media_path(resolved)
    if cdn_url is not None:
        return RedirectResponse(cdn_url, status_code=302)
    return FileResponse(path=str(resolved), media_type="video/mp4", filename=resolved.name)
