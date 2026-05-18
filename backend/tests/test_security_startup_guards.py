from __future__ import annotations

import pytest

from backend.api_gateway.base import _build_services
from backend.execution_worker.base import create_app as create_worker_app
from backend.settings import GatewaySettings
from backend.user_evaluation_service.base import create_app as create_user_eval_app


def test_gateway_settings_generate_ephemeral_secrets_when_unset(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("RL_IDE_AUTH_TOKEN_SECRET", raising=False)
    monkeypatch.delenv("RL_IDE_SHELL_TOKEN_SECRET", raising=False)

    settings = GatewaySettings.from_env()

    assert settings.auth_token_secret
    assert settings.shell_token_secret
    assert settings.auth_token_secret != "dev-auth-secret"
    assert settings.shell_token_secret != "dev-shell-secret"


def test_gateway_rejects_placeholder_auth_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("RL_IDE_AUTH_TOKEN_SECRET", "dev-auth-secret")

    with pytest.raises(ValueError, match="RL_IDE_AUTH_TOKEN_SECRET"):
        GatewaySettings.from_env()


def test_remote_gateway_requires_internal_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("RL_IDE_EXECUTION_MODE", "remote")
    monkeypatch.setenv("RL_IDE_USER_SERVICE_MODE", "remote")
    monkeypatch.delenv("RL_IDE_INTERNAL_TOKEN", raising=False)

    with pytest.raises(ValueError, match="RL_IDE_INTERNAL_TOKEN"):
        _build_services()


def test_execution_worker_requires_internal_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("RL_IDE_INTERNAL_TOKEN", raising=False)

    with pytest.raises(ValueError, match="RL_IDE_INTERNAL_TOKEN"):
        create_worker_app()


def test_user_evaluation_service_requires_internal_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("RL_IDE_INTERNAL_TOKEN", raising=False)

    with pytest.raises(ValueError, match="RL_IDE_INTERNAL_TOKEN"):
        create_user_eval_app()
