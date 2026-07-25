from __future__ import annotations

from lib.schemas.enums import TriggerType

from evaluator.triggers.adherence import AdherenceEvaluator
from evaluator.triggers.base import TriggerEvaluator
from evaluator.triggers.forecast_over_volume import ForecastOverVolumeEvaluator
from evaluator.triggers.sla import SlaEvaluator
from evaluator.triggers.state_duration import StateDurationEvaluator
from evaluator.triggers.tickets import TicketsEvaluator


class TriggerRegistry:
    """Maps ``TriggerType`` values to their concrete ``TriggerEvaluator`` implementations."""

    def __init__(self) -> None:
        self._evaluators: list[TriggerEvaluator] = [
            AdherenceEvaluator(),
            SlaEvaluator(),
            TicketsEvaluator(),
            ForecastOverVolumeEvaluator(),
            StateDurationEvaluator(),
        ]
        self._by_type: dict[TriggerType, TriggerEvaluator] = {
            evaluator.trigger_type: evaluator for evaluator in self._evaluators
        }

    @property
    def evaluators(self) -> list[TriggerEvaluator]:
        """All registered trigger evaluators."""
        return list(self._evaluators)

    def get(self, trigger_type: TriggerType) -> TriggerEvaluator | None:
        """Return the evaluator for ``trigger_type``, or ``None`` if unsupported."""
        return self._by_type.get(trigger_type)
