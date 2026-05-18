from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from threading import Lock
from typing import Any
from uuid import uuid4

from sqlmodel import select

from backend.auth.firebase_admin_setup import FirebaseAdminClient
from backend.auth.roles import AccountStatus, PlatformRole, Principal, parse_role, parse_status
from backend.models.auth_user import AuthUser
from backend.persistence import Database
from backend.services.security_audit_service import SecurityAuditService


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class PlatformTokenService:
    def __init__(self, secret: str, ttl_seconds: int = 43_200) -> None:
        if not secret:
            raise ValueError("Platform token secret cannot be empty.")
        self._secret = secret.encode("utf-8")
        self._ttl_seconds = ttl_seconds

    def issue(self, *, user_id: str, role: PlatformRole) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self._ttl_seconds)
        payload = {
            "sub": user_id,
            "role": role.value,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        encoded_payload = self._encode(payload)
        encoded_signature = self._sign(encoded_payload)
        return f"{encoded_payload}.{encoded_signature}"

    def verify(self, token: str) -> dict[str, Any]:
        payload_segment, signature_segment = self._split(token)
        expected_signature = self._sign(payload_segment)
        if not hmac.compare_digest(expected_signature, signature_segment):
            raise ValueError("Invalid platform token signature.")

        payload_raw = self._decode(payload_segment)
        exp = int(payload_raw.get("exp", 0))
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if exp <= now_ts:
            raise ValueError("Platform token expired.")
        if not payload_raw.get("sub") or not payload_raw.get("role"):
            raise ValueError("Platform token missing required claims.")
        return payload_raw

    def _split(self, token: str) -> tuple[str, str]:
        parts = token.strip().split(".")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Invalid platform token format.")
        return parts[0], parts[1]

    def _encode(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    def _decode(self, segment: str) -> dict[str, Any]:
        padding = "=" * ((4 - len(segment) % 4) % 4)
        raw = base64.urlsafe_b64decode(segment + padding).decode("utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("Invalid platform token payload.")
        return payload

    def _sign(self, encoded_payload: str) -> str:
        digest = hmac.new(
            self._secret,
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


class AuthService:
    def __init__(
        self,
        *,
        database: Database,
        progress_service: Any,
        token_secret: str,
        token_ttl_seconds: int = 43_200,
        firebase_client: FirebaseAdminClient | None = None,
        audit_service: SecurityAuditService | None = None,
        open_provisioning: bool = True,
        allow_legacy_password_sign_in: bool = True,
    ) -> None:
        self._database = database
        self._progress_service = progress_service
        self._token_service = PlatformTokenService(
            token_secret,
            ttl_seconds=token_ttl_seconds,
        )
        self._firebase = firebase_client
        self._audit = audit_service
        self._open_provisioning = open_provisioning
        self._allow_legacy_password_sign_in = allow_legacy_password_sign_in
        self._lock = Lock()
        self._database.create_schema()

    def bootstrap_admin(
        self,
        *,
        firebase_uid: str | None,
        display_name: str = "Platform Admin",
    ) -> None:
        if not firebase_uid:
            return
        normalized = _normalize_display_name(display_name)
        with self._lock:
            with self._database.session() as session:
                statement = select(AuthUser).where(AuthUser.firebase_uid == firebase_uid)
                user = session.exec(statement).first()
                if user is None:
                    user = AuthUser(
                        id=uuid4().hex,
                        firebase_uid=firebase_uid,
                        display_name=normalized or "Platform Admin",
                        normalized_display_name=(normalized or "platform admin").casefold(),
                        role=PlatformRole.ADMIN.value,
                        status=AccountStatus.ACTIVE.value,
                    )
                    session.add(user)
                    session.commit()
                elif user.role != PlatformRole.ADMIN.value:
                    user.role = PlatformRole.ADMIN.value
                    user.updated_at = datetime.now(timezone.utc)
                    session.add(user)
                    session.commit()

    def sign_in(
        self,
        *,
        display_name: str,
        password: str,
        firebase_id_token: str | None = None,
    ) -> tuple[Principal, str]:
        if firebase_id_token:
            user = self._sign_in_with_firebase(
                display_name=display_name,
                firebase_id_token=firebase_id_token,
            )
        else:
            if not self._allow_legacy_password_sign_in:
                raise AuthError(
                    status_code=401,
                    detail="Firebase token required for sign-in.",
                )
            user = self._sign_in_with_legacy_password(
                display_name=display_name,
                password=password,
            )

        principal = self._principal_from_user(user)
        token = self._token_service.issue(user_id=principal.id, role=principal.role)
        self._record_audit(
            actor_user_id=principal.id,
            action="sign_in",
            resource_type="auth_user",
            resource_id=principal.id,
            outcome="success",
        )
        return principal, token

    def authenticate_token(self, token: str) -> Principal:
        platform_error: Exception | None = None
        try:
            claims = self._token_service.verify(token)
            return self._resolve_principal_by_user_id(str(claims["sub"]))
        except Exception as error:  # noqa: BLE001
            platform_error = error

        if self._firebase is None:
            raise AuthError(status_code=401, detail="Invalid authentication token.") from platform_error

        try:
            claims = self._firebase.verify_id_token(token, check_revoked=True)
        except Exception as error:  # noqa: BLE001
            raise AuthError(status_code=401, detail="Invalid Firebase token.") from error
        uid = str(claims.get("uid") or "").strip()
        if not uid:
            raise AuthError(status_code=401, detail="Firebase token missing uid.")
        return self._resolve_principal_by_firebase_uid(uid)

    def sign_out(self, principal: Principal) -> None:
        with self._lock:
            with self._database.session() as session:
                user = session.get(AuthUser, principal.id)
                if user is None:
                    return
                user.revocation_time = datetime.now(timezone.utc)
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                firebase_uid = user.firebase_uid
        if firebase_uid and self._firebase is not None:
            try:
                self._firebase.revoke_refresh_tokens(firebase_uid)
            except Exception:  # pragma: no cover - defensive fallback
                pass

    def list_users(self) -> list[dict[str, Any]]:
        with self._database.session() as session:
            users = session.exec(select(AuthUser).order_by(AuthUser.created_at)).all()
            return [self._serialize_user(user) for user in users]

    def update_user_role(
        self,
        *,
        actor: Principal,
        target_user_id: str,
        role: str,
    ) -> dict[str, Any]:
        if actor.id == target_user_id:
            raise AuthError(
                status_code=400,
                detail="Use a separate admin account for self-role changes.",
            )
        parsed_role = parse_role(role)
        with self._lock:
            with self._database.session() as session:
                user = session.get(AuthUser, target_user_id)
                if user is None:
                    raise AuthError(status_code=404, detail="Unknown user.")
                user.role = parsed_role.value
                user.revocation_time = datetime.now(timezone.utc)
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                session.refresh(user)

        if user.firebase_uid and self._firebase is not None:
            self._firebase.set_role_claim(user.firebase_uid, parsed_role.value)
            self._firebase.revoke_refresh_tokens(user.firebase_uid)

        self._record_audit(
            actor_user_id=actor.id,
            target_user_id=user.id,
            action="role_change",
            resource_type="auth_user",
            resource_id=user.id,
            outcome="success",
            metadata={"new_role": parsed_role.value},
        )
        return self._serialize_user(user)

    def update_user_status(
        self,
        *,
        actor: Principal,
        target_user_id: str,
        status: str,
    ) -> dict[str, Any]:
        parsed_status = parse_status(status)
        with self._lock:
            with self._database.session() as session:
                user = session.get(AuthUser, target_user_id)
                if user is None:
                    raise AuthError(status_code=404, detail="Unknown user.")
                user.status = parsed_status.value
                user.updated_at = datetime.now(timezone.utc)
                if parsed_status == AccountStatus.DISABLED:
                    user.revocation_time = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                session.refresh(user)

        if user.firebase_uid and self._firebase is not None and parsed_status == AccountStatus.DISABLED:
            self._firebase.revoke_refresh_tokens(user.firebase_uid)

        self._record_audit(
            actor_user_id=actor.id,
            target_user_id=user.id,
            action="status_change",
            resource_type="auth_user",
            resource_id=user.id,
            outcome="success",
            metadata={"new_status": parsed_status.value},
        )
        return self._serialize_user(user)

    def _sign_in_with_firebase(
        self,
        *,
        display_name: str,
        firebase_id_token: str,
    ) -> AuthUser:
        if self._firebase is None:
            raise AuthError(
                status_code=503,
                detail="Firebase authentication is unavailable.",
            )
        try:
            decoded = self._firebase.verify_id_token(firebase_id_token, check_revoked=True)
        except Exception as error:  # noqa: BLE001
            raise AuthError(status_code=401, detail="Invalid Firebase token.") from error
        uid = str(decoded.get("uid") or "").strip()
        if not uid:
            raise AuthError(status_code=401, detail="Firebase token missing uid.")
        profile_name = _normalize_display_name(
            str(decoded.get("name") or decoded.get("email") or display_name or "Student")
        )
        return self._find_or_provision_user_for_uid(uid=uid, display_name=profile_name)

    def _sign_in_with_legacy_password(
        self,
        *,
        display_name: str,
        password: str,
    ) -> AuthUser:
        dashboard = self._progress_service.sign_in(display_name, password)
        student = (dashboard or {}).get("student", {})
        student_id = str(student.get("id") or "").strip()
        if not student_id:
            raise AuthError(status_code=500, detail="Sign-in failed to resolve learner identity.")
        normalized_name = _normalize_display_name(
            str(student.get("display_name") or display_name or "Student")
        )
        with self._lock:
            with self._database.session() as session:
                user = session.get(AuthUser, student_id)
                if user is None:
                    user = AuthUser(
                        id=student_id,
                        firebase_uid=None,
                        display_name=normalized_name,
                        normalized_display_name=normalized_name.casefold(),
                        role=PlatformRole.STUDENT.value,
                        status=AccountStatus.ACTIVE.value,
                    )
                else:
                    user.display_name = normalized_name
                    user.normalized_display_name = normalized_name.casefold()
                    user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user

    def _find_or_provision_user_for_uid(self, *, uid: str, display_name: str) -> AuthUser:
        with self._lock:
            with self._database.session() as session:
                user = session.exec(select(AuthUser).where(AuthUser.firebase_uid == uid)).first()
                if user is None:
                    lookup = display_name.casefold()
                    user = session.exec(
                        select(AuthUser)
                        .where(AuthUser.firebase_uid.is_(None))
                        .where(AuthUser.normalized_display_name == lookup)
                    ).first()
                    if user is not None:
                        user.firebase_uid = uid
                        user.display_name = display_name
                        user.normalized_display_name = lookup
                    elif self._open_provisioning:
                        user = AuthUser(
                            id=uid,
                            firebase_uid=uid,
                            display_name=display_name,
                            normalized_display_name=lookup,
                            role=PlatformRole.STUDENT.value,
                            status=AccountStatus.ACTIVE.value,
                        )
                    else:
                        raise AuthError(
                            status_code=403,
                            detail="Account is not provisioned for this Firebase user.",
                        )
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
                session.refresh(user)

        if parse_role(user.role) == PlatformRole.STUDENT:
            self._ensure_student_progress_record(user.id, user.display_name)
        return user

    def _resolve_principal_by_user_id(self, user_id: str) -> Principal:
        with self._database.session() as session:
            user = session.get(AuthUser, user_id)
            if user is None:
                raise AuthError(status_code=401, detail="Authentication token subject is unknown.")
            return self._principal_from_user(user)

    def _resolve_principal_by_firebase_uid(self, uid: str) -> Principal:
        with self._database.session() as session:
            user = session.exec(select(AuthUser).where(AuthUser.firebase_uid == uid)).first()
            if user is None:
                raise AuthError(status_code=403, detail="Authenticated user is not provisioned.")
            return self._principal_from_user(user)

    def _principal_from_user(self, user: AuthUser) -> Principal:
        status = parse_status(user.status)
        if status != AccountStatus.ACTIVE:
            raise AuthError(status_code=403, detail="User account is disabled.")
        role = parse_role(user.role)
        if role == PlatformRole.STUDENT:
            self._ensure_student_progress_record(user.id, user.display_name)
        return Principal(
            id=user.id,
            role=role,
            status=status,
            firebase_uid=user.firebase_uid,
        )

    def _ensure_student_progress_record(self, student_id: str, display_name: str) -> None:
        ensure_record = getattr(self._progress_service, "ensure_student_record", None)
        if callable(ensure_record):
            ensure_record(student_id=student_id, display_name=display_name)

    def _serialize_user(self, user: AuthUser) -> dict[str, Any]:
        return {
            "id": user.id,
            "firebase_uid": user.firebase_uid,
            "display_name": user.display_name,
            "role": user.role,
            "status": user.status,
            "revocation_time": (
                user.revocation_time.isoformat() if user.revocation_time is not None else None
            ),
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

    def _record_audit(self, **kwargs: Any) -> None:
        if self._audit is None:
            return
        self._audit.record(**kwargs)


def _normalize_display_name(display_name: str) -> str:
    normalized = " ".join((display_name or "").split())
    return normalized or "Student"
