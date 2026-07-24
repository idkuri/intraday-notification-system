from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from lib.schemas.enums import TriggerType
from lib.schemas.events import Event
from lib.schemas.rules import RuleRead


@dataclass(frozen=True)
class TriggerMatch:
    """Result of evaluating one rule trigger against an event.

    Attributes:
        entity_key: Stable key for the entity being monitored (e.g. ``queue:q1``).
        title: Notification title when ``condition_true`` is ``True``; otherwise empty.
        body: Notification body when ``condition_true`` is ``True``; otherwise empty.
        condition_true: Whether the rule's trigger condition is currently satisfied.
        violation_window_id: Optional identifier for the active violation window,
            used to deduplicate repeated firings within the same window.
    """

    entity_key: str
    title: str
    body: str
    condition_true: bool
    violation_window_id: str | None = None


class TriggerEvaluator(ABC):
    """Evaluates a single trigger type against incoming events."""

    @property
    @abstractmethod
    def trigger_type(self) -> TriggerType:
        """The trigger type this evaluator handles."""

    @abstractmethod
    def evaluate(self, event: Event, rule: RuleRead) -> TriggerMatch | None:
        """Evaluate an event against a rule.

        Args:
            event: Incoming domain event to inspect.
            rule: Rule definition including threshold, scope, and trigger config.

        Returns:
            A ``TriggerMatch`` describing whether the condition holds, or ``None`` when
            ``event`` is not the expected type for this evaluator.
        """
