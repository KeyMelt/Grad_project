"""DigitalOcean Spaces media publishing.

The project only needs a tiny subset of S3: public object uploads with cache
headers and deterministic CDN URLs. Keeping this client in stdlib avoids
adding boto3 to the backend image just for media publishing.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import http.client
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from manim_service import settings


class SpacesConfigError(RuntimeError):
    """Raised when Spaces publishing is enabled but not fully configured."""


class SpacesUploadError(RuntimeError):
    """Raised when DigitalOcean rejects an object upload."""


@dataclass(frozen=True)
class SpacesConfig:
    region: str
    bucket: str
    endpoint: str
    cdn_url: str
    access_key: str
    secret_key: str

    @classmethod
    def from_settings(cls) -> SpacesConfig:
        return cls(
            region=settings.DO_SPACES_REGION,
            bucket=settings.DO_SPACES_BUCKET,
            endpoint=settings.DO_SPACES_ENDPOINT.rstrip("/"),
            cdn_url=settings.DO_SPACES_CDN_URL.rstrip("/"),
            access_key=settings.DO_SPACES_ACCESS_KEY,
            secret_key=settings.DO_SPACES_SECRET_KEY,
        )

    def validate(self) -> None:
        missing = [
            name
            for name, value in (
                ("DO_SPACES_REGION", self.region),
                ("DO_SPACES_BUCKET", self.bucket),
                ("DO_SPACES_ENDPOINT", self.endpoint),
                ("DO_SPACES_CDN_URL", self.cdn_url),
                ("DO_SPACES_ACCESS_KEY", self.access_key),
                ("DO_SPACES_SECRET_KEY", self.secret_key),
            )
            if not value
        ]
        if missing:
            raise SpacesConfigError(
                "Spaces publishing is enabled but these variables are missing: "
                + ", ".join(missing)
            )


def spaces_enabled() -> bool:
    return settings.MEDIA_STORAGE_BACKEND == "spaces"


def public_url(object_key: str) -> str | None:
    if not spaces_enabled() or not settings.DO_SPACES_CDN_URL:
        return None
    return f"{settings.DO_SPACES_CDN_URL.rstrip('/')}/{object_key.lstrip('/')}"


def upload_public_file(
    local_path: Path,
    object_key: str,
    *,
    cache_control: str = "public, max-age=31536000, immutable",
) -> str | None:
    """Upload a local file to Spaces and return its CDN URL when enabled."""
    if not spaces_enabled():
        return None
    config = SpacesConfig.from_settings()
    config.validate()
    client = DigitalOceanSpacesClient(config)
    client.upload_public_file(local_path, object_key, cache_control=cache_control)
    return public_url(object_key)


class DigitalOceanSpacesClient:
    def __init__(self, config: SpacesConfig) -> None:
        self.config = config
        parsed = urlparse(config.endpoint)
        self.scheme = parsed.scheme or "https"
        self.host = parsed.netloc or parsed.path
        if self.scheme != "https":
            raise SpacesConfigError("DO_SPACES_ENDPOINT must use https.")

    def upload_public_file(
        self,
        local_path: Path,
        object_key: str,
        *,
        cache_control: str,
    ) -> None:
        if not local_path.is_file():
            raise FileNotFoundError(f"Media file not found: {local_path}")
        body = local_path.read_bytes()
        canonical_uri = f"/{self.config.bucket}/{object_key.lstrip('/')}"
        headers = {
            "cache-control": cache_control,
            "content-type": _content_type(local_path),
            "host": self.host,
            "x-amz-acl": "public-read",
            "x-amz-content-sha256": hashlib.sha256(body).hexdigest(),
            "x-amz-date": _amz_date(),
        }
        headers["authorization"] = self._authorization_header(
            method="PUT",
            canonical_uri=canonical_uri,
            headers=headers,
        )
        headers["content-length"] = str(len(body))

        conn = http.client.HTTPSConnection(self.host, timeout=60)
        conn.request("PUT", canonical_uri, body=body, headers=headers)
        response = conn.getresponse()
        response_body = response.read().decode(errors="replace")
        if response.status not in (200, 201):
            raise SpacesUploadError(
                f"Spaces upload failed for {object_key!r}: "
                f"{response.status} {response.reason} {response_body[:500]}"
            )

    def _authorization_header(
        self,
        *,
        method: str,
        canonical_uri: str,
        headers: dict[str, str],
    ) -> str:
        signed_header_names = sorted(headers)
        signed_headers = ";".join(signed_header_names)
        canonical_headers = "".join(
            f"{name}:{headers[name].strip()}\n" for name in signed_header_names
        )
        payload_hash = headers["x-amz-content-sha256"]
        canonical_request = "\n".join(
            [method, canonical_uri, "", canonical_headers, signed_headers, payload_hash]
        )
        date_stamp = headers["x-amz-date"][:8]
        scope = f"{date_stamp}/{self.config.region}/s3/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                headers["x-amz-date"],
                scope,
                hashlib.sha256(canonical_request.encode()).hexdigest(),
            ]
        )
        signing_key = _signing_key(self.config.secret_key, date_stamp, self.config.region)
        signature = hmac.new(
            signing_key,
            string_to_sign.encode(),
            hashlib.sha256,
        ).hexdigest()
        return (
            "AWS4-HMAC-SHA256 "
            f"Credential={self.config.access_key}/{scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )


def _amz_date() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def _signing_key(secret_key: str, date_stamp: str, region: str) -> bytes:
    date_key = _sign(("AWS4" + secret_key).encode(), date_stamp)
    region_key = _sign(date_key, region)
    service_key = _sign(region_key, "s3")
    return _sign(service_key, "aws4_request")


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode(), hashlib.sha256).digest()


def _content_type(path: Path) -> str:
    if path.suffix.lower() == ".vtt":
        return "text/vtt"
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"
