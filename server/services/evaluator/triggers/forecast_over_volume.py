from __future__ import annotations

from lib.schemas.enums import TriggerType
from lib.schemas.events import Event, QueueSnapshotEvent
from lib.schemas.rules import RuleRead

from evaluator.triggers.base import TriggerEvaluator, TriggerMatch


class ForecastOverVolumeEvaluator(TriggerEvaluator):
    """Fires when forecast is at/above ``threshold`` percent of recent volume."""

    @property
    def trigger_type(self) -> TriggerType:
        return TriggerType.QUEUE_FORECAST_OVER_VOLUME

    def evaluate(self, event: Event, rule: RuleRead) -> TriggerMatch | None:
        """Compare ``volume_forecast_next_15m`` to ``volume_last_15m`` * threshold%.

        Args:
            event: Expected to be a ``QueueSnapshotEvent``; other types yield ``None``.
            rule: Rule whose ``threshold`` is the minimum percent of recent volume
                (e.g. 130 means forecast must be >= 1.3 * last-15m volume).

        Returns:
            A ``TriggerMatch`` with ``condition_true`` when forecast is high vs recent,
            or ``None`` when ``event`` is the wrong type.
        """
        if not isinstance(event, QueueSnapshotEvent):
            return None

        entity_key = f"queue:{event.queue_id}"
        threshold = rule.threshold or 0
        last = event.volume_last_15m
        forecast = event.volume_forecast_next_15m

        if forecast is None:
            condition_true = False
            pct_of_recent: int | None = None
        elif last <= 0:
            condition_true = forecast > 0
            pct_of_recent = None
        else:
            condition_true = forecast * 100 >= last * threshold
            pct_of_recent = (forecast * 100) // last

        if not condition_true:
            return TriggerMatch(
                entity_key=entity_key,
                title="",
                body="",
                condition_true=False,
            )

        title = f"Forecast above recent: {event.queue_id}"
        if pct_of_recent is None:
            body = (
                f"Queue {event.queue_id} forecast {forecast} with recent volume "
                f"{last} (threshold {threshold}%)"
            )
        else:
            body = (
                f"Queue {event.queue_id} forecast {forecast} vs recent volume "
                f"{last} ({pct_of_recent}% of recent, threshold {threshold}%)"
            )
        return TriggerMatch(
            entity_key=entity_key,
            title=title,
            body=body,
            condition_true=True,
        )
