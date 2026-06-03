from __future__ import annotations

import pytest

from backend.persistence import Database
from backend.services.auth_service import AuthError, AuthService


class _FakeProgressService:
    def sign_in(self, display_name: str, password: str):
        del password
        return {
            "student": {
                "id": "student-1",
                "display_name": display_name,
            }
        }

    def ensure_student_record(self, *, student_id: str, display_name: str):
        del student_id, display_name


def test_sign_out_revokes_platform_token(tmp_path):
    service = AuthService(
        database=Database(database_url=f"sqlite:///{tmp_path / 'auth.db'}"),
        progress_service=_FakeProgressService(),
        token_secret="test-token-secret",
        allow_legacy_password_sign_in=True,
    )
    principal, token = service.sign_in(display_name="Maya", password="good")

    assert service.authenticate_token(token).id == principal.id

    service.sign_out(principal)

    with pytest.raises(AuthError, match="Invalid authentication token") as error:
        service.authenticate_token(token)
    assert isinstance(error.value.__cause__, AuthError)
    assert "revoked" in error.value.__cause__.detail
