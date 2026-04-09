from __future__ import annotations

import os

import uvicorn


if __name__ == "__main__":
    port = int(os.getenv("RL_IDE_EXECUTION_WORKER_PORT", "8100"))
    reload_enabled = os.getenv("RL_IDE_BACKEND_RELOAD", "").lower() in {
        "1",
        "true",
        "yes",
    }
    uvicorn.run(
        "backend.execution_worker.base:create_app",
        host="127.0.0.1",
        port=port,
        reload=reload_enabled,
        factory=True,
    )
