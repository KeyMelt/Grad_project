import os

import uvicorn


if __name__ == "__main__":
    reload_enabled = os.getenv("RL_IDE_BACKEND_RELOAD", "").lower() in {
        "1",
        "true",
        "yes",
    }
    uvicorn.run(
        "backend.api_gateway.base:create_app",
        host="127.0.0.1",
        port=8000,
        reload=reload_enabled,
        factory=True,
    )
