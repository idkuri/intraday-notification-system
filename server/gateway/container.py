from __future__ import annotations

import lib.models  # noqa: F401
from lib.db.session import DatabaseSessionManager
from sqlalchemy.orm import Session

from evaluator.notification_dedup_store import create_notification_dedup_store
from evaluator.rule_engine import RuleEngine
from ingest.ingest_service import IngestService
from notifications.notification_service import NotificationService
from rules.rule_service import RuleService


class AppContainer:
    """Single composition root. Used by FastAPI lifespan AND event_streamer CLI."""

    def __init__(self, db_url: str = "sqlite:///./data/assembled.db") -> None:
        self.db = DatabaseSessionManager(db_url)

    def session(self) -> Session:
        """Create a new unmanaged SQLAlchemy session."""
        return self.db.session_factory()()

    def rule_service(self, session: Session) -> RuleService:
        """Build a rule service bound to the given session."""
        return RuleService(session)

    def notification_service(self, session: Session) -> NotificationService:
        """Build a notification service bound to the given session."""
        return NotificationService(session)

    def engine(self, session: Session) -> RuleEngine:
        """Build a rule engine with the production notification-dedup store."""
        return RuleEngine(create_notification_dedup_store(session))

    def ingest_service(self, session: Session) -> IngestService:
        """Build the ingest pipeline for the given session."""
        return IngestService(
            self.rule_service(session),
            self.engine(session),
            self.notification_service(session),
        )
