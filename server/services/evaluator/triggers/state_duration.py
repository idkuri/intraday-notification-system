from __future__ import annotations

from lib.schemas.enums import TriggerType
from lib.schemas.events import AgentStateChangeEvent, Event
from lib.schemas.rules import RuleRead

from evaluator.triggers.base import TriggerEvaluator, TriggerMatch


class StateDurationEvaluator(TriggerEvaluator):
    """Fires when an agent stayed in ``rule.target_state`` long enough."""

    @property
    def trigger_type(self) -> TriggerType:
        return TriggerType.AGENT_STATE_DURATION

    def evaluate(self, event: Event, rule: RuleRead) -> TriggerMatch | None:
        """Check previous-state duration on an ``AgentStateChangeEvent``.

        Args:
            event: Expected to be an ``AgentStateChangeEvent``; other types yield ``None``.
            rule: Rule whose ``target_state`` and ``threshold`` define the condition.

        Returns:
            A ``TriggerMatch`` with ``condition_true`` when the prior state duration meets
            the threshold, or ``None`` when ``event`` is the wrong type.
        """
        if not isinstance(event, AgentStateChangeEvent):
            return None

        entity_key = f"agent:{event.agent_id}"
        threshold = rule.threshold or 0
        target_state = rule.target_state.value if rule.target_state is not None else ""

        condition_true = (
            event.previous_state == target_state and event.previous_state_duration_sec >= threshold
        )

        if not condition_true:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
            )

        title = f"Long {event.previous_state}: {event.agent_id}"
        body = (
            f"Agent {event.agent_id} was {event.previous_state} for "
            f"{event.previous_state_duration_sec}s (threshold {threshold}s); "
            f"now {event.new_state}"
        )
        return TriggerMatch(
            entity_key=entity_key,
            title=title,
            body=body,
            condition_true=True,
        )
