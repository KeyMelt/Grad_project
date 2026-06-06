from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from backend.settings import GatewaySettings


def _concept_video_root() -> Path:
    return GatewaySettings.from_env().concept_video_dir.resolve()


def _cdn_concept_video_url(filename: str, settings: GatewaySettings) -> str | None:
    if not settings.media_cdn_url:
        return None
    return f"{settings.media_cdn_url}/concept_videos/{filename}"


def _ensure_production_media_available(settings: GatewaySettings) -> None:
    if not settings.is_production:
        return
    if not settings.media_cdn_url:
        raise HTTPException(
            status_code=503,
            detail="Production concept-video CDN URL is not configured.",
        )


def _allow_local_media_fallback(settings: GatewaySettings) -> bool:
    return settings.allow_local_media_fallback and not settings.is_production


def _validate_concept_video_filename(filename: str) -> str:
    if "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid concept video filename.")
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only MP4 video and VTT caption files can be served.",
        )
    return suffix


_ALLOWED_EXTENSIONS: dict[str, str] = {
    ".mp4": "video/mp4",
    ".vtt": "text/vtt",
}


def _resolve_concept_video(filename: str) -> tuple[Path, str]:
    suffix = _validate_concept_video_filename(filename)
    media_type = _ALLOWED_EXTENSIONS[suffix]

    file_path = (_concept_video_root() / filename).resolve()
    try:
        file_path.relative_to(_concept_video_root())
    except ValueError as error:
        raise HTTPException(
            status_code=403,
            detail="Concept video path is outside the configured media directory.",
        ) from error

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Concept video file not found.")
    return file_path, media_type


def build_concept_videos_router() -> APIRouter:
    router = APIRouter()

    @router.get("/media/concept-videos/{filename}")
    def concept_video(filename: str):
        settings = GatewaySettings.from_env()
        _validate_concept_video_filename(filename)
        _ensure_production_media_available(settings)
        cdn_url = _cdn_concept_video_url(filename, settings)
        if cdn_url is not None:
            return RedirectResponse(cdn_url, status_code=302)
        if not _allow_local_media_fallback(settings):
            raise HTTPException(
                status_code=503,
                detail="Concept-video media is not configured for this environment.",
            )
        file_path, media_type = _resolve_concept_video(filename)
        headers = {"Cache-Control": "public, max-age=3600"}
        if media_type == "text/vtt":
            headers["Access-Control-Allow-Origin"] = "*"
        return FileResponse(file_path, media_type=media_type, headers=headers)

    return router
