from __future__ import annotations

import uvicorn

from backend.settings import RuntimeSettings

if __name__ == "__main__":
    settings = RuntimeSettings.from_env()
    uvicorn.run(
        "backend.execution_worker.base:create_app",
        host=settings.backend_host,
        port=settings.execution_worker_port,
        reload=settings.backend_reload,
        factory=True,
    )
