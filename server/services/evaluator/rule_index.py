from __future__ import annotations

from lib.schemas.enums import EventType, TriggerType
from lib.schemas.events import (
    AdherenceCheckEvent,
    AgentStateChangeEvent,
    Event,
    QueueSnapshotEvent,
)
from lib.schemas.rules import RuleRead

_QUEUE_TRIGGERS = frozenset(
    {
        TriggerType.QUEUE_SLA_BREACHED,
        TriggerType.QUEUE_TICKETS_WAITING,
        TriggerType.QUEUE_FORECAST_OVER_VOLUME,
    }
)
_AGENT_TRIGGERS = frozenset(
    {TriggerType.ADHERENCE_VIOLATION_DURATION, TriggerType.AGENT_STATE_DURATION}
)

_EVENT_TRIGGER_TYPES: dict[EventType, frozenset[TriggerType]] = {
    EventType.QUEUE_SNAPSHOT: _QUEUE_TRIGGERS,
    EventType.AGENT_STATE_CHANGE: frozenset({TriggerType.AGENT_STATE_DURATION}),
    EventType.ADHERENCE_CHECK: frozenset({TriggerType.ADHERENCE_VIOLATION_DURATION}),
}


def _queue_scope_matches(rule: RuleRead, queue_id: str) -> bool:
    """Return True when ``queue_id`` is listed in the rule's queue scope."""
    queue_ids = rule.scope.queue_ids
    if not queue_ids:
        return False
    return queue_id in queue_ids


def _agent_scope_matches(rule: RuleRead, agent_id: str, event_queue_ids: list[str] | None) -> bool:
    """Return True when agent/queue scope constraints match the event."""
    scope = rule.scope
    agent_ok = scope.agent_id is None or scope.agent_id == agent_id
    if scope.queue_ids is None:
        queue_ok = True
    elif not event_queue_ids:
        queue_ok = False
    else:
        queue_ok = bool(set(scope.queue_ids) & set(event_queue_ids))
    return agent_ok and queue_ok


class RuleIndex:
    """Indexes enabled rules for fast candidate lookup by event type."""

    def __init__(self, rules: list[RuleRead]) -> None:
        self._rules = [rule for rule in rules if rule.enabled]

    def candidates(self, event: Event) -> list[RuleRead]:
        """Return enabled rules whose trigger type and scope match the event.

        Scope matching:
            - Queue triggers require a ``QueueSnapshotEvent`` whose ``queue_id`` is in
              ``rule.scope.queue_ids`` (non-empty list required).
            - Agent triggers require an ``AdherenceCheckEvent`` or ``AgentStateChangeEvent``
              whose ``agent_id`` matches ``rule.scope.agent_id`` when set, and whose
              ``queue_ids`` overlap ``rule.scope.queue_ids`` when that scope is set.

        Args:
            event: Incoming event to match against indexed rules.

        Returns:
            Rules eligible for trigger evaluation against ``event``.
        """
        event_type = EventType(event.type)
        eligible_types = _EVENT_TRIGGER_TYPES.get(event_type, frozenset())
        matched: list[RuleRead] = []

        for rule in self._rules:
            if rule.trigger_type not in eligible_types:
                continue
            if rule.trigger_type in _QUEUE_TRIGGERS:
                if isinstance(event, QueueSnapshotEvent) and _queue_scope_matches(
                    rule, event.queue_id
                ):
                    matched.append(rule)
            elif (
                rule.trigger_type in _AGENT_TRIGGERS
                and isinstance(event, AdherenceCheckEvent | AgentStateChangeEvent)
                and _agent_scope_matches(rule, event.agent_id, event.queue_ids)
            ):
                matched.append(rule)

        return matched
