"""FastAPI app for `manim_service`.

Routes:
- `POST /render/concept-video`
- `POST /render/trace`
- `GET  /jobs/{job_id}`
- `GET  /videos/{filename}`
- `GET  /health`

When the configured queue backend is "memory", the app also starts an
in-process render worker on its lifespan so the service is fully functional
out of a single process. In production (`QUEUE_BACKEND=redis`) the worker
would run as a separate process.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Response, status

from manim_service import settings
from manim_service.api.routes import concept_videos, traces
from manim_service.jobs import worker
from manim_service.storage import output as storage

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    storage.ensure_subdirs()
    thread = None
    stop_event = None
    if settings.QUEUE_BACKEND == "memory":
        thread, stop_event = worker.start_background_worker()
        logger.info("manim_service: started in-process render worker")
    try:
        yield
    finally:
        if stop_event is not None:
            stop_event.set()
        if thread is not None:
            thread.join(timeout=5.0)


def create_app() -> FastAPI:
    app = FastAPI(title="manim_service", version="0.1.0", lifespan=lifespan)
    app.include_router(concept_videos.router)
    app.include_router(traces.router)

    @app.get("/health")
    def health(response: Response) -> dict[str, object]:
        runtime = settings.render_runtime_status()
        missing = [name for name, path in runtime.items() if path is None]
        if missing:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "ok" if not missing else "degraded",
            "queue_backend": settings.QUEUE_BACKEND,
            "render_runtime": runtime,
            "missing": missing,
        }

    return app


app = create_app()
