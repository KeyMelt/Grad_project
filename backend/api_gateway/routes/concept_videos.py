from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.settings import GatewaySettings


def _concept_video_root() -> Path:
    return GatewaySettings.from_env().concept_video_dir.resolve()


def _resolve_concept_video(filename: str) -> Path:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid concept video filename.")
    if Path(filename).suffix.lower() != ".mp4":
        raise HTTPException(status_code=400, detail="Only MP4 concept videos can be served.")

    video_path = (_concept_video_root() / filename).resolve()
    try:
        video_path.relative_to(_concept_video_root())
    except ValueError as error:
        raise HTTPException(
            status_code=403,
            detail="Concept video path is outside the configured media directory.",
        ) from error

    if not video_path.exists() or not video_path.is_file():
        raise HTTPException(status_code=404, detail="Concept video file not found.")
    return video_path


def build_concept_videos_router() -> APIRouter:
    router = APIRouter()

    @router.get("/media/concept-videos/{filename}")
    def concept_video(filename: str):
        return FileResponse(
            _resolve_concept_video(filename),
            media_type="video/mp4",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    return router
