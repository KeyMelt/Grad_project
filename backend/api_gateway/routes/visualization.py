from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from backend.settings import GatewaySettings


def _animation_output_root() -> Path:
    return GatewaySettings.from_env().visualization_output_dir.resolve()


def _resolve_visualization_path(path: str, *, suffix: str, label: str) -> Path:
    target_path = Path(path).expanduser().resolve()
    output_root = _animation_output_root()
    if target_path.suffix.lower() != suffix:
        raise HTTPException(status_code=400, detail=f"Only {label} files can be served.")
    try:
        target_path.relative_to(output_root)
    except ValueError as error:
        raise HTTPException(
            status_code=403,
            detail=f"{label} path is outside the visualization output directory.",
        ) from error
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail=f"{label} file not found.")
    return target_path


def build_visualization_router() -> APIRouter:
    router = APIRouter()

    @router.get("/visualization/frame")
    def visualization_frame(path: str = Query(..., min_length=1)):
        frame_path = _resolve_visualization_path(path, suffix=".png", label="Frame")
        return FileResponse(frame_path, media_type="image/png")

    @router.get("/visualization/video")
    def visualization_video(path: str = Query(..., min_length=1)):
        video_path = _resolve_visualization_path(path, suffix=".mp4", label="Video")
        return FileResponse(video_path, media_type="video/mp4")

    return router
