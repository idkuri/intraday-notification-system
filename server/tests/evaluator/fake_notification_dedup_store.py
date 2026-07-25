from __future__ import annotations

from collections.abc import Sequence

from lib.schemas.notification_dedup import NotificationDedupRead

from evaluator.ports import NotificationDedupStore


class FakeNotificationDedupStore(NotificationDedupStore):
    """Dict-backed ``NotificationDedupStore`` for unit tests (no DB)."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], NotificationDedupRead] = {}

    def get(self, rule_id: str, entity_key: str) -> NotificationDedupRead:
        return self._store.get(
            (rule_id, entity_key),
            NotificationDedupRead(rule_id=rule_id, entity_key=entity_key),
        )

    def save(self, state: NotificationDedupRead) -> None:
        self._store[(state.rule_id, state.entity_key)] = state

    def load_for_rules(
        self, rule_ids: Sequence[str]
    ) -> dict[tuple[str, str], NotificationDedupRead]:
        wanted = set(rule_ids)
        return {key: state for key, state in self._store.items() if key[0] in wanted}
