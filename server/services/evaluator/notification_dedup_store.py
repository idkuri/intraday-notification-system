from __future__ import annotations

from collections.abc import Sequence

from lib.models.notification_dedup import NotificationDedupModel
from lib.schemas.notification_dedup import (
    NotificationDedupCreate,
    NotificationDedupRead,
    NotificationDedupUpdate,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from evaluator.ports import NotificationDedupStore


def create_notification_dedup_store(session: Session) -> NotificationDedupStore:
    """Build the SQLAlchemy-backed store used by ``RuleEngine`` in production."""
    return _SessionNotificationDedupStore(session)


class _SessionNotificationDedupStore(NotificationDedupStore):
    """Persists prior condition/window rows in ``notification_dedup``."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, rule_id: str, entity_key: str) -> NotificationDedupRead:
        row = self._session.get(NotificationDedupModel, (rule_id, entity_key))
        if row is None:
            return NotificationDedupRead(rule_id=rule_id, entity_key=entity_key)
        return row.to_schema()

    def save(self, state: NotificationDedupRead) -> None:
        row = self._session.get(NotificationDedupModel, (state.rule_id, state.entity_key))
        if row is None:
            self._session.add(
                NotificationDedupModel.from_create(
                    NotificationDedupCreate(
                        rule_id=state.rule_id,
                        entity_key=state.entity_key,
                        last_condition_true=state.last_condition_true,
                        last_violation_window_id=state.last_violation_window_id,
                    )
                )
            )
        else:
            row.apply_update(
                NotificationDedupUpdate(
                    last_condition_true=state.last_condition_true,
                    last_violation_window_id=state.last_violation_window_id,
                )
            )
        self._session.flush()

    def load_for_rules(
        self, rule_ids: Sequence[str]
    ) -> dict[tuple[str, str], NotificationDedupRead]:
        if not rule_ids:
            return {}
        rows = self._session.scalars(
            select(NotificationDedupModel).where(
                NotificationDedupModel.rule_id.in_(tuple(rule_ids))
            )
        ).all()
        return {(row.rule_id, row.entity_key): row.to_schema() for row in rows}
