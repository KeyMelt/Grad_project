from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from backend.settings import GatewaySettings


def _concept_video_root() -> Path:
    return GatewaySettings.from_env().concept_video_dir.resolve()


def _cdn_concept_video_url(filename: str) -> str:
    settings = GatewaySettings.from_env()
    if settings.media_storage_backend != "spaces":
        raise HTTPException(status_code=503, detail="Media storage must be DigitalOcean Spaces.")
    if not settings.media_cdn_url:
        raise HTTPException(status_code=503, detail="DO_SPACES_CDN_URL is not configured.")
    return f"{settings.media_cdn_url}/concept_videos/{filename}"


_ALLOWED_EXTENSIONS: dict[str, str] = {
    ".mp4": "video/mp4",
    ".vtt": "text/vtt",
}


def _resolve_concept_video(filename: str) -> tuple[Path, str]:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid concept video filename.")
    suffix = Path(filename).suffix.lower()
    media_type = _ALLOWED_EXTENSIONS.get(suffix)
    if media_type is None:
        raise HTTPException(
            status_code=400,
            detail="Only MP4 video and VTT caption files can be served.",
        )

    return _concept_video_root() / filename, media_type


def build_concept_videos_router() -> APIRouter:
    router = APIRouter()

    @router.get("/media/concept-videos/{filename}")
    def concept_video(filename: str):
        _resolve_concept_video(filename)
        cdn_url = _cdn_concept_video_url(filename)
        return RedirectResponse(cdn_url, status_code=302)

    return router
