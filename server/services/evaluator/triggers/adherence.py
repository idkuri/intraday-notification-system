from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional

from lib.schemas.enums import TriggerType
from lib.schemas.events import AdherenceCheckEvent, Event
from lib.schemas.rules import RuleRead

from evaluator.triggers.base import TriggerEvaluator, TriggerMatch


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class AdherenceEvaluator(TriggerEvaluator):
    """Fires when an agent remains out of adherence longer than ``rule.threshold`` seconds."""

    @property
    def trigger_type(self) -> TriggerType:
        return TriggerType.ADHERENCE_VIOLATION_DURATION

    def evaluate(self, event: Event, rule: RuleRead) -> Optional[TriggerMatch]:
        """Check adherence violation duration on an ``AdherenceCheckEvent``.

        Args:
            event: Expected to be an ``AdherenceCheckEvent``; other types yield ``None``.
            rule: Rule whose ``threshold`` is the minimum violation duration in seconds.

        Returns:
            A ``TriggerMatch`` with ``condition_true`` when elapsed violation time meets
            the threshold, or ``None`` when ``event`` is the wrong type.
        """
        if not isinstance(event, AdherenceCheckEvent):
            return None

        entity_key = f"agent:{event.agent_id}"
        threshold = rule.threshold or 0

        if not event.in_violation or event.violation_started_at is None:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
            )

        elapsed = (_to_utc(event.ts) - _to_utc(event.violation_started_at)).total_seconds()
        condition_true = elapsed >= threshold
        violation_window_id = event.violation_started_at.isoformat()

        if not condition_true:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
                violation_window_id=violation_window_id,
            )

        title = f"Adherence violation: {event.agent_id}"
        body = (
            f"Agent {event.agent_id} out of adherence for {elapsed:.0f}s "
            f"(threshold {threshold}s). "
            f"scheduled={event.scheduled_state} actual={event.actual_state}"
        )
        return TriggerMatch(
            entity_key=entity_key,
            title=title,
            body=body,
            condition_true=True,
            violation_window_id=violation_window_id,
        )
