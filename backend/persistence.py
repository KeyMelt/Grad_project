from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.settings import DatabaseSettings


class Database:
    """Thin SQLModel wrapper with sensible local defaults."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or DatabaseSettings.from_env().database_url
        self._closed = False
        engine_kwargs: dict = {}

        if self.database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            if self.database_url in {"sqlite://", "sqlite:///:memory:"}:
                engine_kwargs["poolclass"] = StaticPool
            else:
                engine_kwargs["poolclass"] = NullPool

        self.engine = create_engine(self.database_url, **engine_kwargs)

    def create_schema(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self.engine) as session:
            yield session

    def close(self) -> None:
        if self._closed:
            return
        self.engine.dispose()
        self._closed = True

    def __del__(self) -> None:  # pragma: no cover - defensive cleanup
        try:
            self.close()
        except Exception:
            pass
