from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from lib.schemas.notification_dedup import NotificationDedupRead


class NotificationDedupStore(ABC):
    """Loads/saves prior condition/window rows keyed by ``(rule_id, entity_key)``."""

    @abstractmethod
    def get(self, rule_id: str, entity_key: str) -> NotificationDedupRead:
        """Load the row for a rule/entity pair.

        Returns:
            The persisted row, or an empty default when none exists.
        """

    @abstractmethod
    def save(self, state: NotificationDedupRead) -> None:
        """Upsert prior condition/window for a rule/entity pair."""

    @abstractmethod
    def load_for_rules(
        self, rule_ids: Sequence[str]
    ) -> dict[tuple[str, str], NotificationDedupRead]:
        """Load all rows for the given rule IDs in one query.

        Returns:
            Map of ``(rule_id, entity_key)`` → state for rows that exist.
        """
