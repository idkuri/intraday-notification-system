from __future__ import annotations

from lib.schemas.enums import TriggerType
from lib.schemas.events import Event, QueueSnapshotEvent
from lib.schemas.rules import RuleRead

from evaluator.triggers.base import TriggerEvaluator, TriggerMatch


class TicketsEvaluator(TriggerEvaluator):
    """Fires when tickets waiting in a queue reach or exceed ``rule.threshold``."""

    @property
    def trigger_type(self) -> TriggerType:
        return TriggerType.QUEUE_TICKETS_WAITING

    def evaluate(self, event: Event, rule: RuleRead) -> TriggerMatch | None:
        """Compare ``tickets_waiting`` to ``rule.threshold`` on a ``QueueSnapshotEvent``.

        Args:
            event: Expected to be a ``QueueSnapshotEvent``; other types yield ``None``.
            rule: Rule whose ``threshold`` is the minimum backlog count.

        Returns:
            A ``TriggerMatch`` with ``condition_true`` when backlog meets threshold, or
            ``None`` when ``event`` is the wrong type.
        """
        if not isinstance(event, QueueSnapshotEvent):
            return None

        entity_key = f"queue:{event.queue_id}"
        threshold = rule.threshold or 0
        condition_true = event.tickets_waiting >= threshold

        if not condition_true:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
            )

        title = f"High backlog: {event.queue_id}"
        body = (
            f"Queue {event.queue_id} has {event.tickets_waiting} tickets waiting "
            f"(threshold {threshold})"
        )
        return TriggerMatch(
            entity_key=entity_key,
            title=title,
            body=body,
            condition_true=True,
        )
