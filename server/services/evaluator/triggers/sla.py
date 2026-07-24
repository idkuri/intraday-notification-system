from __future__ import annotations

from lib.schemas.enums import TriggerType
from lib.schemas.events import Event, QueueSnapshotEvent
from lib.schemas.rules import RuleRead

from evaluator.triggers.base import TriggerEvaluator, TriggerMatch


class SlaEvaluator(TriggerEvaluator):
    """Fires when a queue snapshot shows longest wait exceeding the SLA target."""

    @property
    def trigger_type(self) -> TriggerType:
        return TriggerType.QUEUE_SLA_BREACHED

    def evaluate(self, event: Event, rule: RuleRead) -> TriggerMatch | None:
        """Compare ``longest_wait_sec`` to ``sla_target_sec`` on a ``QueueSnapshotEvent``.

        Args:
            event: Expected to be a ``QueueSnapshotEvent``; other types yield ``None``.
            rule: Rule metadata (threshold unused; SLA comes from the event).

        Returns:
            A ``TriggerMatch`` with ``condition_true`` when wait exceeds SLA, or ``None``
            when ``event`` is the wrong type.
        """
        if not isinstance(event, QueueSnapshotEvent):
            return None

        entity_key = f"queue:{event.queue_id}"
        condition_true = event.longest_wait_sec >= event.sla_target_sec

        if not condition_true:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
            )

        title = f"SLA breached: {event.queue_id}"
        body = (
            f"Queue {event.queue_id} longest_wait={event.longest_wait_sec}s "
            f"exceeds sla_target={event.sla_target_sec}s; "
            f"tickets_waiting={event.tickets_waiting}"
        )
        return TriggerMatch(
            entity_key=entity_key,
            title=title,
            body=body,
            condition_true=True,
        )
