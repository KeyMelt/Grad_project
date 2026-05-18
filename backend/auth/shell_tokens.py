from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json


class ShellTokenService:
    _SESSION_KIND = "workspace_shell"
    _LAUNCH_KIND = "workspace_launch"

    def __init__(self, secret: str) -> None:
        if not secret:
            raise ValueError("Shell token secret cannot be empty.")
        self._secret = secret.encode("utf-8")

    def issue(
        self,
        *,
        user_id: str,
        role: str,
        session_id: str,
        ttl_seconds: int = 300,
    ) -> str:
        return self._issue_token(
            user_id=user_id,
            role=role,
            session_id=session_id,
            ttl_seconds=ttl_seconds,
            kind=self._SESSION_KIND,
        )

    def issue_launch(
        self,
        *,
        user_id: str,
        role: str,
        session_id: str,
        ttl_seconds: int = 300,
    ) -> str:
        return self._issue_token(
            user_id=user_id,
            role=role,
            session_id=session_id,
            ttl_seconds=ttl_seconds,
            kind=self._LAUNCH_KIND,
        )

    def _issue_token(
        self,
        *,
        user_id: str,
        role: str,
        session_id: str,
        ttl_seconds: int,
        kind: str,
    ) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        payload = {
            "kind": kind,
            "user_id": user_id,
            "role": role,
            "session_id": session_id,
            "exp": int(expires_at.timestamp()),
        }
        encoded_payload = self._encode_payload(payload)
        signature = hmac.new(
            self._secret,
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        encoded_signature = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
        return f"{encoded_payload}.{encoded_signature}"

    def verify(self, token: str) -> dict[str, str]:
        return self._verify_token(token, expected_kind=self._SESSION_KIND)

    def verify_launch(self, token: str) -> dict[str, str]:
        return self._verify_token(token, expected_kind=self._LAUNCH_KIND)

    def _verify_token(
        self,
        token: str,
        *,
        expected_kind: str,
    ) -> dict[str, str]:
        payload_segment, signature_segment = self._split_token(token)
        expected_signature = hmac.new(
            self._secret,
            payload_segment.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        observed_signature = self._decode_segment(signature_segment)
        if not hmac.compare_digest(expected_signature, observed_signature):
            raise ValueError("Invalid shell token signature.")

        payload_raw = self._decode_segment(payload_segment).decode("utf-8")
        payload = json.loads(payload_raw)
        expires_at = int(payload.get("exp", 0))
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if expires_at <= now_ts:
            raise ValueError("Shell token expired.")
        session_id = str(payload.get("session_id") or "").strip()
        user_id = str(payload.get("user_id") or "").strip()
        role = str(payload.get("role") or "").strip()
        if not session_id or not user_id or not role:
            raise ValueError("Shell token missing required fields.")
        kind = str(payload.get("kind") or self._SESSION_KIND).strip()
        if kind != expected_kind:
            raise ValueError("Shell token has the wrong purpose.")
        return {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
        }

    def _split_token(self, token: str) -> tuple[str, str]:
        parts = token.strip().split(".")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Invalid shell token format.")
        return parts[0], parts[1]

    def _encode_payload(self, payload: dict[str, object]) -> str:
        raw = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    def _decode_segment(self, segment: str) -> bytes:
        padding = "=" * ((4 - len(segment) % 4) % 4)
        return base64.urlsafe_b64decode(segment + padding)
