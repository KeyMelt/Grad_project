from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from backend.auth.dependencies import (
    assert_owner_or_admin,
    build_optional_principal_dependency,
)
from backend.auth.roles import PlatformRole, Principal
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


def _task_snapshot_or_404(services: Any, task_id: str) -> dict[str, Any]:
    snapshot = services.execution.snapshot(task_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"Unknown task_id '{task_id}'.")
    return snapshot


def _ensure_task_owner(services: Any, task_id: str, principal: Principal) -> dict[str, Any]:
    snapshot = _task_snapshot_or_404(services, task_id)
    owner_user_id = str(snapshot.get("owner_user_id") or "")
    assert_owner_or_admin(principal=principal, owner_user_id=owner_user_id)
    return snapshot


def _artifact_path_from_snapshot(
    snapshot: dict[str, Any],
    *,
    kind: str,
    suffix: str,
    label: str,
) -> Path:
    artifacts = snapshot.get("artifacts")
    if not isinstance(artifacts, list):
        raise HTTPException(status_code=404, detail=f"No {label.lower()} artifact available.")
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        if artifact.get("artifact_kind") != kind:
            continue
        return _resolve_visualization_path(
            str(artifact.get("artifact_path") or ""),
            suffix=suffix,
            label=label,
        )
    raise HTTPException(status_code=404, detail=f"No {label.lower()} artifact available.")


def build_visualization_router(services: Any) -> APIRouter:
    router = APIRouter()
    optional_principal = build_optional_principal_dependency(auth_service=services.auth)

    def _resolve_principal(
        *,
        principal: Principal | None,
    ) -> Principal:
        effective_principal = principal
        if effective_principal is None:
            raise HTTPException(status_code=401, detail="Authentication required.")
        if effective_principal.role not in {
            PlatformRole.STUDENT,
            PlatformRole.INSTRUCTOR,
            PlatformRole.ADMIN,
        }:
            raise HTTPException(status_code=403, detail="Insufficient role for artifact access.")
        return effective_principal

    @router.get("/artifacts/tasks/{task_id}/video")
    def task_video_artifact(
        task_id: str,
        principal: Principal | None = Depends(optional_principal),
    ):
        resolved_principal = _resolve_principal(
            principal=principal,
        )
        snapshot = _ensure_task_owner(services, task_id, resolved_principal)
        artifact_path = _artifact_path_from_snapshot(
            snapshot,
            kind="replay_video",
            suffix=".mp4",
            label="Video",
        )
        return FileResponse(artifact_path, media_type="video/mp4")

    @router.get("/visualization/frame")
    def visualization_frame(
        path: str = Query(..., min_length=1),
        principal: Principal | None = Depends(optional_principal),
    ):
        _resolve_principal(principal=principal)
        frame_path = _resolve_visualization_path(path, suffix=".png", label="Frame")
        return FileResponse(frame_path, media_type="image/png")

    @router.get("/visualization/video")
    def visualization_video(
        path: str = Query(..., min_length=1),
        principal: Principal | None = Depends(optional_principal),
    ):
        _resolve_principal(principal=principal)
        video_path = _resolve_visualization_path(path, suffix=".mp4", label="Video")
        return FileResponse(video_path, media_type="video/mp4")

    return router
