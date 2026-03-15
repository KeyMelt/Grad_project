import os

import uvicorn

from backend.api_gateway.base import app


if __name__ == "__main__":
    reload_enabled = os.getenv("RL_IDE_BACKEND_RELOAD", "").lower() in {
        "1",
        "true",
        "yes",
    }
    uvicorn.run(
        "backend.api_gateway.base:app",
        host="127.0.0.1",
        port=8000,
        reload=reload_enabled,
    )
