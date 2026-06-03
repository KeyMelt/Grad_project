from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Cookie, Depends, Header, HTTPException, status

from backend.auth.roles import PlatformRole, Principal
from backend.settings import GatewaySettings


def build_current_principal_dependency(
    *,
    auth_service: Any,
    audit_service: Any | None = None,
) -> Callable[..., Principal]:
    def _dependency(
        authorization: Annotated[str | None, Header()] = None,
        session_cookie: Annotated[
            str | None,
            Cookie(alias=GatewaySettings.from_env().session_cookie_name),
        ] = None,
    ) -> Principal:
        token = _extract_auth_token(authorization, session_cookie)
        try:
            return auth_service.authenticate_token(token)
        except Exception as error:  # noqa: BLE001
            if audit_service is not None:
                try:
                    audit_service.record(
                        actor_user_id="anonymous",
                        action="access_denied",
                        resource_type="auth",
                        outcome="failure",
                        metadata={"reason": str(error)},
                    )
                except Exception:  # pragma: no cover - defensive audit fallback
                    pass
            if hasattr(error, "status_code") and hasattr(error, "detail"):
                raise HTTPException(status_code=error.status_code, detail=error.detail) from error
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
            ) from error

    return _dependency


def build_optional_principal_dependency(
    *,
    auth_service: Any,
) -> Callable[..., Principal | None]:
    def _dependency(
        authorization: Annotated[str | None, Header()] = None,
        session_cookie: Annotated[
            str | None,
            Cookie(alias=GatewaySettings.from_env().session_cookie_name),
        ] = None,
    ) -> Principal | None:
        if not authorization and not session_cookie:
            return None
        token = _extract_auth_token(authorization, session_cookie)
        try:
            return auth_service.authenticate_token(token)
        except Exception:  # noqa: BLE001
            return None

    return _dependency


def require_roles(
    current_principal_dependency: Callable[..., Principal],
    *roles: PlatformRole,
) -> Callable[..., Principal]:
    allowed = {role.value for role in roles}

    def _dependency(
        principal: Principal = Depends(current_principal_dependency),
    ) -> Principal:
        if principal.role.value not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this operation.",
            )
        return principal

    return _dependency


def assert_owner_or_admin(
    *,
    principal: Principal,
    owner_user_id: str,
) -> None:
    if principal.role == PlatformRole.ADMIN:
        return
    if owner_user_id == principal.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this resource.",
    )


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be Bearer <token>.",
        )
    return token.strip()


def _extract_auth_token(authorization: str | None, session_cookie: str | None) -> str:
    if authorization:
        return _extract_bearer_token(authorization)
    if session_cookie and session_cookie.strip():
        return session_cookie.strip()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials.",
    )
