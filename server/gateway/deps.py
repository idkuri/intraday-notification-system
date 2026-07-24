from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from gateway.container import AppContainer
from ingest.ingest_service import IngestService
from notifications.notification_service import NotificationService
from rules.rule_service import RuleService

_container: Optional[AppContainer] = None


def set_container(container: AppContainer) -> None:
    """Register the application composition root for dependency injection."""
    global _container
    _container = container


def get_container_or_none() -> Optional[AppContainer]:
    """Return the registered container, or ``None`` before startup."""
    return _container


def get_container() -> AppContainer:
    """Return the registered container, raising if startup has not run."""
    if _container is None:
        raise RuntimeError("App container has not been initialized")
    return _container


def get_session() -> Iterator[Session]:
    """Yield a request-scoped SQLAlchemy session with commit/rollback handling."""
    yield from get_container().db.get_session()


def get_actor_username(
    x_username: Annotated[Optional[str], Header(alias="X-Username")] = None,
) -> str:
    """Extract and validate the acting user from the ``X-Username`` header."""
    if x_username is None or not x_username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username required via X-Username header",
        )
    username = x_username.strip()
    if len(username) > 64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at most 64 characters",
        )
    return username


def get_rule_service(session: Session = Depends(get_session)) -> RuleService:
    """Request-scoped rule application service."""
    return RuleService(session)


def get_notification_service(
    session: Session = Depends(get_session),
) -> NotificationService:
    """Request-scoped notification application service."""
    return NotificationService(session)


def get_ingest_service(session: Session = Depends(get_session)) -> IngestService:
    """Request-scoped ingest pipeline."""
    return get_container().ingest_service(session)
