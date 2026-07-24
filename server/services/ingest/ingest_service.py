from __future__ import annotations

from lib.schemas.events import Event
from lib.schemas.ingest import IngestEventResponse
from sqlalchemy.orm import Session

from evaluator.rule_engine import RuleEngine
from notifications.notification_service import NotificationService
from rules.rule_service import RuleService


class IngestService:
    """Orchestrates rule evaluation and notification delivery for ingested events."""

    def __init__(
        self,
        rule_service: RuleService,
        engine: RuleEngine,
        notification_service: NotificationService,
    ) -> None:
        self._rule_service = rule_service
        self._engine = engine
        self._notification_service = notification_service

    @property
    def session(self) -> Session:
        """SQLAlchemy session shared with the notification service."""
        return self._notification_service._session

    def reset_state(self) -> None:
        """Clear persisted notifications and notification-dedup memory."""
        self._notification_service.clear_all()
        self._notification_service.clear_notification_dedup()

    def ingest_event(self, event: Event) -> IngestEventResponse:
        """Evaluate enabled rules against one event and deliver any notifications.

        Args:
            event: Discriminated queue/agent/adherence event to evaluate.

        Returns:
            ``IngestEventResponse`` with ``notifications_emitted`` count and
            ``notification_ids`` of rows persisted for this event. Does not commit;
            the session owner commits.
        """
        rules = self._rule_service.list_enabled_rules()
        creates = self._engine.evaluate_event(event, rules)
        ids: list[str] = []
        for create in creates:
            notification = self._notification_service.record_and_deliver(create)
            ids.append(notification.id)
        return IngestEventResponse(notifications_emitted=len(ids), notification_ids=ids)
