from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from lib.schemas.enums import TriggerType
from lib.schemas.events import Event
from lib.schemas.notification_dedup import NotificationDedupRead
from lib.schemas.notifications import NotificationCreate
from lib.schemas.rules import RuleRead

from evaluator.ports import NotificationDedupStore
from evaluator.rule_index import RuleIndex
from evaluator.triggers import TriggerRegistry
from evaluator.triggers.base import TriggerMatch


class RuleEngine:
    """Indexes rules, runs trigger matchers, and applies become-true / window noise control."""

    def __init__(self, dedup_store: NotificationDedupStore) -> None:
        self._registry = TriggerRegistry()
        self._dedup = dedup_store
        self._cache: Optional[dict[tuple[str, str], NotificationDedupRead]] = None

    def evaluate_event(self, event: Event, rules: list[RuleRead]) -> list[NotificationCreate]:
        """Evaluate an event against all candidate rules.

        Args:
            event: Incoming domain event to process.
            rules: Full rule set; only enabled rules matching the event are considered.

        Returns:
            Notification create payloads for matches that passed become-true / window
            checks (one payload per allowed rule match).
        """
        index = RuleIndex(rules)
        candidates = index.candidates(event)
        self._begin_event([rule.id for rule in candidates])
        creates: list[NotificationCreate] = []

        for rule in candidates:
            evaluator = self._registry.get(rule.trigger_type)
            if evaluator is None:
                continue

            match = evaluator.evaluate(event, rule)
            if match is None:
                continue

            if not self._should_notify(rule, match):
                continue

            creates.append(
                NotificationCreate(
                    rule_id=rule.id,
                    recipient_id=rule.owner_id,
                    title=match.title,
                    body=match.body,
                    severity=rule.severity,
                    entity_key=match.entity_key,
                    triggering_event_id=event.event_id,
                    ts=event.ts,
                    channels=rule.channels,
                )
            )

        return creates

    def _begin_event(self, rule_ids: Sequence[str]) -> None:
        """Prefetch dedup rows for ``rule_ids`` so checks avoid per-match SELECTs."""
        self._cache = dict(self._dedup.load_for_rules(rule_ids))

    def _should_notify(self, rule: RuleRead, match: TriggerMatch) -> bool:
        """Decide whether a match may produce a notification; persist updated memory.

        1. Condition false -> clear become-true memory, deny.
        2. Same adherence ``violation_window_id`` -> deny.
        3. Non-state-duration and condition already true -> deny.
        4. Else persist true/window -> allow.

        ``AGENT_STATE_DURATION`` skips step 3 (events are already transitions).
        """
        prior = self._get(rule.id, match.entity_key)

        if not match.condition_true:
            self._put(
                NotificationDedupRead(
                    rule_id=rule.id,
                    entity_key=match.entity_key,
                    last_condition_true=False,
                    last_violation_window_id=prior.last_violation_window_id,
                )
            )
            return False

        if (
            match.violation_window_id is not None
            and match.violation_window_id == prior.last_violation_window_id
        ):
            return False

        if rule.trigger_type is not TriggerType.AGENT_STATE_DURATION and prior.last_condition_true:
            return False

        self._put(
            NotificationDedupRead(
                rule_id=rule.id,
                entity_key=match.entity_key,
                last_condition_true=True,
                last_violation_window_id=(
                    match.violation_window_id
                    if match.violation_window_id is not None
                    else prior.last_violation_window_id
                ),
            )
        )
        return True

    def _get(self, rule_id: str, entity_key: str) -> NotificationDedupRead:
        key = (rule_id, entity_key)
        if self._cache is not None:
            cached = self._cache.get(key)
            if cached is not None:
                return cached
            return NotificationDedupRead(rule_id=rule_id, entity_key=entity_key)
        return self._dedup.get(rule_id, entity_key)

    def _put(self, state: NotificationDedupRead) -> None:
        if self._cache is not None:
            self._cache[(state.rule_id, state.entity_key)] = state
        self._dedup.save(state)
