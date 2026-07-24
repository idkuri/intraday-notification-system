from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from lib.db.base import Base


def _enable_sqlite_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
    """SQLite disables FK enforcement unless PRAGMA foreign_keys=ON per connection."""
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseSessionManager:
    """Owns the SQLAlchemy engine, session factory, and schema lifecycle."""

    def __init__(self, url: str = "sqlite:///./data/assembled.db") -> None:
        if url.startswith("sqlite:///./"):
            relative = url.removeprefix("sqlite:///./")
            Path(relative).parent.mkdir(parents=True, exist_ok=True)
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self._engine = create_engine(url, connect_args=connect_args)
        if url.startswith("sqlite"):
            event.listen(self._engine, "connect", _enable_sqlite_foreign_keys)
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def create_all(self) -> None:
        """Create all tables registered on the declarative base."""
        Base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        """Drop all tables registered on the declarative base."""
        Base.metadata.drop_all(self._engine)

    def session_factory(self) -> sessionmaker[Session]:
        """Return the configured SQLAlchemy session factory."""
        return self._session_factory

    def get_session(self) -> Iterator[Session]:
        """Yield a session that commits on success and rolls back on error."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
