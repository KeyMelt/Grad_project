from __future__ import annotations

import uvicorn

from backend.settings import RuntimeSettings

if __name__ == "__main__":
    settings = RuntimeSettings.from_env()
    uvicorn.run(
        "backend.user_evaluation_service.base:create_app",
        host=settings.backend_host,
        port=settings.user_evaluation_port,
        reload=settings.backend_reload,
        factory=True,
    )
