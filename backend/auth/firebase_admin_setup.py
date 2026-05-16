from __future__ import annotations

from typing import Any

try:  # pragma: no cover - import availability depends on runtime environment
    import firebase_admin
    from firebase_admin import auth, credentials
except Exception:  # pragma: no cover
    firebase_admin = None
    auth = None
    credentials = None


class FirebaseAdminClient:
    def __init__(
        self,
        *,
        credentials_path: str | None,
        app_name: str,
    ) -> None:
        if firebase_admin is None or auth is None:
            raise RuntimeError("firebase-admin is not available.")
        self._app = self._get_or_create_app(
            credentials_path=credentials_path,
            app_name=app_name,
        )

    def verify_id_token(self, token: str, *, check_revoked: bool = True) -> dict[str, Any]:
        return auth.verify_id_token(
            token,
            app=self._app,
            check_revoked=check_revoked,
        )

    def set_role_claim(self, uid: str, role: str) -> None:
        auth.set_custom_user_claims(uid, {"role": role}, app=self._app)

    def revoke_refresh_tokens(self, uid: str) -> None:
        auth.revoke_refresh_tokens(uid, app=self._app)

    def lookup_display_name(self, uid: str) -> str | None:
        user = auth.get_user(uid, app=self._app)
        return user.display_name or user.email

    def _get_or_create_app(
        self,
        *,
        credentials_path: str | None,
        app_name: str,
    ) -> Any:
        try:
            return firebase_admin.get_app(app_name)
        except ValueError:
            pass

        cred = credentials.Certificate(credentials_path) if credentials_path else None
        if cred is None:
            return firebase_admin.initialize_app(name=app_name)
        return firebase_admin.initialize_app(credential=cred, name=app_name)
