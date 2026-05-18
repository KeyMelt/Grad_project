from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PlatformRole(StrEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Principal:
    id: str
    role: PlatformRole
    status: AccountStatus
    firebase_uid: str | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == PlatformRole.ADMIN


def parse_role(raw_role: str | None) -> PlatformRole:
    try:
        return PlatformRole((raw_role or "").strip().lower())
    except ValueError as error:
        raise ValueError(f"Unsupported role '{raw_role}'.") from error


def parse_status(raw_status: str | None) -> AccountStatus:
    try:
        return AccountStatus((raw_status or "").strip().lower())
    except ValueError as error:
        raise ValueError(f"Unsupported account status '{raw_status}'.") from error
