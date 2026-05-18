from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}
PLACEHOLDER_SECRET_VALUES = {
    "change-me",
    "change-this-local-dev-auth-secret",
    "change-this-local-dev-shell-secret",
    "change-this-local-dev-token",
    "dev-auth-secret",
    "dev-shell-secret",
}
_RUNTIME_SECRET_CACHE: dict[str, str] = {}


def env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    value = raw_value.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return default


def env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    return int(raw_value)


def env_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    return float(raw_value)


def env_str(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return default if value is None else value.strip()


def env_path(name: str, default: str) -> Path:
    return Path(env_str(name, default)).expanduser()


def env_csv(name: str, default: str = "") -> list[str]:
    raw = env_str(name, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def is_placeholder_secret(value: str | None) -> bool:
    normalized = (value or "").strip().lower()
    return bool(normalized) and normalized in PLACEHOLDER_SECRET_VALUES


def runtime_secret(name: str) -> str:
    configured = env_str(name)
    if configured:
        if is_placeholder_secret(configured):
            raise ValueError(
                f"{name} must be set to a non-placeholder value or left unset for an ephemeral secret."
            )
        return configured

    cached = _RUNTIME_SECRET_CACHE.get(name)
    if cached is None:
        cached = secrets.token_urlsafe(48)
        _RUNTIME_SECRET_CACHE[name] = cached
    return cached


def require_configured_secret(name: str, purpose: str) -> str:
    configured = env_str(name)
    if not configured:
        raise ValueError(f"{name} must be configured for {purpose}.")
    if is_placeholder_secret(configured):
        raise ValueError(f"{name} must not use a placeholder value for {purpose}.")
    return configured


@dataclass(frozen=True)
class GatewaySettings:
    user_service_mode: str
    user_service_url: str
    user_service_timeout_seconds: float
    firebase_credentials_path: str | None
    firebase_app_name: str
    execution_mode: str
    execution_worker_url: str
    worker_timeout_seconds: float
    internal_token: str | None
    visualization_output_dir: Path
    concept_video_dir: Path
    cors_allowed_origins: list[str]
    auth_token_secret: str
    auth_token_ttl_seconds: int
    shell_token_secret: str
    open_provisioning: bool
    allow_legacy_password_sign_in: bool
    bootstrap_admin_firebase_uid: str | None
    bootstrap_admin_display_name: str

    @classmethod
    def from_env(cls) -> GatewaySettings:
        internal_token = env_str("RL_IDE_INTERNAL_TOKEN") or None
        firebase_credentials = env_str("RL_IDE_FIREBASE_CREDENTIALS_PATH") or None
        bootstrap_uid = env_str("RL_IDE_BOOTSTRAP_ADMIN_FIREBASE_UID") or None
        cors_origins = env_csv("RL_IDE_ALLOWED_ORIGINS")
        if not cors_origins:
            cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        return cls(
            user_service_mode=env_str("RL_IDE_USER_SERVICE_MODE", "local").lower(),
            user_service_url=env_str(
                "RL_IDE_USER_SERVICE_URL",
                "http://127.0.0.1:8200",
            ),
            user_service_timeout_seconds=env_float(
                "RL_IDE_USER_SERVICE_TIMEOUT_SECONDS",
                10.0,
            ),
            firebase_credentials_path=firebase_credentials,
            firebase_app_name=env_str("RL_IDE_FIREBASE_APP_NAME", "rl-ide-backend"),
            execution_mode=env_str("RL_IDE_EXECUTION_MODE", "local").lower(),
            execution_worker_url=env_str(
                "RL_IDE_EXECUTION_WORKER_URL",
                "http://127.0.0.1:8100",
            ),
            worker_timeout_seconds=env_float("RL_IDE_WORKER_TIMEOUT_SECONDS", 10.0),
            internal_token=internal_token,
            visualization_output_dir=env_path(
                "RL_IDE_VISUALIZATION_OUTPUT_DIR",
                "backend/visualization/animations",
            ),
            concept_video_dir=env_path(
                "RL_IDE_CONCEPT_VIDEO_DIR",
                "backend/media/concept_videos",
            ),
            cors_allowed_origins=cors_origins,
            auth_token_secret=runtime_secret("RL_IDE_AUTH_TOKEN_SECRET"),
            auth_token_ttl_seconds=env_int("RL_IDE_AUTH_TOKEN_TTL_SECONDS", 43_200),
            shell_token_secret=runtime_secret("RL_IDE_SHELL_TOKEN_SECRET"),
            open_provisioning=env_bool("RL_IDE_OPEN_PROVISIONING", True),
            allow_legacy_password_sign_in=env_bool(
                "RL_IDE_ALLOW_LEGACY_PASSWORD_SIGN_IN",
                True,
            ),
            bootstrap_admin_firebase_uid=bootstrap_uid,
            bootstrap_admin_display_name=env_str(
                "RL_IDE_BOOTSTRAP_ADMIN_DISPLAY_NAME",
                "Platform Admin",
            ),
        )


@dataclass(frozen=True)
class WorkerSettings:
    job_store_path: Path
    artifact_store_path: Path
    workspace_store_path: Path
    workspace_base_dir: str | None
    workspace_image: str
    workspace_use_docker: bool
    internal_token: str | None

    @classmethod
    def from_env(cls) -> WorkerSettings:
        internal_token = env_str("RL_IDE_INTERNAL_TOKEN") or None
        return cls(
            job_store_path=env_path(
                "RL_IDE_JOB_STORE_PATH",
                "backend/data/execution_jobs.db",
            ),
            artifact_store_path=env_path(
                "RL_IDE_ARTIFACT_STORE_PATH",
                "backend/data/execution_artifacts.db",
            ),
            workspace_store_path=env_path(
                "RL_IDE_WORKSPACE_STORE_PATH",
                "backend/data/workspace_state.db",
            ),
            workspace_base_dir=env_str("RL_IDE_WORKSPACE_BASE_DIR") or None,
            workspace_image=env_str("RL_IDE_WORKSPACE_IMAGE", "python:3.11-slim"),
            workspace_use_docker=env_bool("RL_IDE_WORKSPACE_USE_DOCKER", True),
            internal_token=internal_token,
        )


@dataclass(frozen=True)
class RuntimeSettings:
    backend_host: str
    gateway_port: int
    execution_worker_port: int
    user_evaluation_port: int
    backend_reload: bool

    @classmethod
    def from_env(cls) -> RuntimeSettings:
        return cls(
            backend_host=env_str("RL_IDE_BACKEND_HOST", "127.0.0.1"),
            gateway_port=env_int("RL_IDE_GATEWAY_PORT", 8000),
            execution_worker_port=env_int("RL_IDE_EXECUTION_WORKER_PORT", 8100),
            user_evaluation_port=env_int("RL_IDE_USER_EVALUATION_PORT", 8200),
            backend_reload=env_bool("RL_IDE_BACKEND_RELOAD", False),
        )


@dataclass(frozen=True)
class ExecutionSettings:
    logger_dir: str
    visualization_output_dir: str
    timeout_base_seconds: int
    timeout_per_episode_seconds: int
    timeout_max_seconds: int

    @classmethod
    def from_env(cls) -> ExecutionSettings:
        return cls(
            logger_dir=env_str("RL_IDE_LOGGER_DIR", "backend/logger/logs"),
            visualization_output_dir=str(
                env_path(
                    "RL_IDE_VISUALIZATION_OUTPUT_DIR",
                    "backend/visualization/animations",
                )
            ),
            timeout_base_seconds=env_int("RL_IDE_EXECUTION_TIMEOUT_BASE_SECONDS", 300),
            timeout_per_episode_seconds=env_int(
                "RL_IDE_EXECUTION_TIMEOUT_PER_EPISODE_SECONDS",
                5,
            ),
            timeout_max_seconds=env_int("RL_IDE_EXECUTION_TIMEOUT_MAX_SECONDS", 900),
        )


@dataclass(frozen=True)
class VisualizationSettings:
    output_dir: str
    manim_python_path: str
    manim_timeout_seconds: int

    @classmethod
    def from_env(cls) -> VisualizationSettings:
        return cls(
            output_dir=str(
                env_path(
                    "RL_IDE_VISUALIZATION_OUTPUT_DIR",
                    "backend/visualization/animations",
                )
            ),
            manim_python_path=env_str(
                "RL_IDE_MANIM_PYTHON",
                "/Users/ultramarine/.venvs/manim/bin/python3",
            ),
            manim_timeout_seconds=env_int("RL_IDE_MANIM_TIMEOUT_SECONDS", 300),
        )


@dataclass(frozen=True)
class DatabaseSettings:
    database_url: str

    @classmethod
    def from_env(cls) -> DatabaseSettings:
        configured = env_str("RL_IDE_DB_URL")
        if configured:
            return cls(database_url=configured)

        database_path = Path(__file__).resolve().parent / "data" / "rl_learning_platform.db"
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return cls(database_url=f"sqlite:///{database_path}")


@dataclass(frozen=True)
class UserEvaluationSettings:
    firebase_credentials_path: str | None
    firebase_app_name: str

    @classmethod
    def from_env(cls) -> UserEvaluationSettings:
        credentials_path = env_str("RL_IDE_FIREBASE_CREDENTIALS_PATH") or None
        return cls(
            firebase_credentials_path=credentials_path,
            firebase_app_name=env_str("RL_IDE_FIREBASE_APP_NAME", "rl-ide-backend"),
        )
