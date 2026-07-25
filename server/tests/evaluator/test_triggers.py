from __future__ import annotations

from datetime import UTC, datetime, timedelta

from lib.schemas.enums import AgentState, TriggerType
from lib.schemas.events import (
    AdherenceCheckEvent,
    AgentStateChangeEvent,
    QueueSnapshotEvent,
)

from evaluator.triggers.adherence import AdherenceEvaluator
from evaluator.triggers.sla import SlaEvaluator
from evaluator.triggers.state_duration import StateDurationEvaluator
from evaluator.triggers.tickets import TicketsEvaluator
from tests.conftest import make_rule_read


def _ts(offset_sec: int = 0) -> datetime:
    return datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=offset_sec)


class TestAdherenceEvaluator:
    def setup_method(self) -> None:
        self.evaluator = AdherenceEvaluator()
        self.rule = make_rule_read(
            trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
            scope=make_rule_read().scope.model_copy(update={"agent_id": "a_19", "queue_ids": None}),
            threshold=600,
        )

    def test_condition_true_when_elapsed_at_or_above_threshold(self) -> None:
        violation_started = _ts(0)
        event = AdherenceCheckEvent(
            event_id="e1",
            ts=_ts(600),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="on_break",
            in_violation=True,
            violation_started_at=violation_started,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is True
        assert match.entity_key == "agent:a_19"
        assert match.violation_window_id == violation_started.isoformat()

    def test_condition_false_when_elapsed_below_threshold(self) -> None:
        violation_started = _ts(0)
        event = AdherenceCheckEvent(
            event_id="e2",
            ts=_ts(300),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="on_break",
            in_violation=True,
            violation_started_at=violation_started,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is False
        assert match.violation_window_id == violation_started.isoformat()

    def test_returns_none_for_non_adherence_event(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e3",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=5,
            longest_wait_sec=100,
            sla_target_sec=60,
            agents_available=2,
            agents_on_call=1,
            volume_last_15m=10,
            volume_forecast_next_15m=12,
        )

        assert self.evaluator.evaluate(event, self.rule) is None


class TestSlaEvaluator:
    def setup_method(self) -> None:
        self.evaluator = SlaEvaluator()
        self.rule = make_rule_read(trigger_type=TriggerType.QUEUE_SLA_BREACHED)

    def test_condition_true_when_longest_wait_at_or_above_sla_target(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e4",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=3,
            longest_wait_sec=120,
            sla_target_sec=120,
            agents_available=1,
            agents_on_call=0,
            volume_last_15m=5,
            volume_forecast_next_15m=6,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is True
        assert match.entity_key == "queue:billing"

    def test_condition_false_when_longest_wait_below_sla_target(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e5",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=3,
            longest_wait_sec=59,
            sla_target_sec=60,
            agents_available=1,
            agents_on_call=0,
            volume_last_15m=5,
            volume_forecast_next_15m=6,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is False

    def test_returns_none_for_non_queue_snapshot_event(self) -> None:
        event = AdherenceCheckEvent(
            event_id="e6",
            ts=_ts(),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="on_break",
            in_violation=False,
        )

        assert self.evaluator.evaluate(event, self.rule) is None


class TestTicketsEvaluator:
    def setup_method(self) -> None:
        self.evaluator = TicketsEvaluator()
        self.rule = make_rule_read(
            trigger_type=TriggerType.QUEUE_TICKETS_WAITING,
            threshold=20,
        )

    def test_condition_true_when_tickets_waiting_at_or_above_threshold(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e7",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=25,
            longest_wait_sec=30,
            sla_target_sec=60,
            agents_available=1,
            agents_on_call=0,
            volume_last_15m=5,
            volume_forecast_next_15m=6,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is True
        assert "25" in match.body

    def test_condition_false_when_tickets_waiting_below_threshold(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e8",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=10,
            longest_wait_sec=30,
            sla_target_sec=60,
            agents_available=1,
            agents_on_call=0,
            volume_last_15m=5,
            volume_forecast_next_15m=6,
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is False


class TestStateDurationEvaluator:
    def setup_method(self) -> None:
        self.evaluator = StateDurationEvaluator()
        self.rule = make_rule_read(
            trigger_type=TriggerType.AGENT_STATE_DURATION,
            scope=make_rule_read().scope.model_copy(update={"agent_id": "a_42", "queue_ids": None}),
            threshold=2700,
            target_state=AgentState.ON_CALL,
        )

    def test_condition_true_when_previous_state_matches_and_duration_at_threshold(self) -> None:
        event = AgentStateChangeEvent(
            event_id="e9",
            ts=_ts(),
            type="agent_state_change",
            agent_id="a_42",
            queue_ids=["billing"],
            previous_state="on_call",
            previous_state_duration_sec=2700,
            new_state="available",
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is True
        assert match.entity_key == "agent:a_42"

    def test_condition_false_when_duration_below_threshold(self) -> None:
        event = AgentStateChangeEvent(
            event_id="e10",
            ts=_ts(),
            type="agent_state_change",
            agent_id="a_42",
            queue_ids=["billing"],
            previous_state="on_call",
            previous_state_duration_sec=1000,
            new_state="available",
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is False

    def test_condition_false_when_previous_state_does_not_match_target(self) -> None:
        event = AgentStateChangeEvent(
            event_id="e11",
            ts=_ts(),
            type="agent_state_change",
            agent_id="a_42",
            queue_ids=["billing"],
            previous_state="on_break",
            previous_state_duration_sec=5000,
            new_state="available",
        )

        match = self.evaluator.evaluate(event, self.rule)

        assert match is not None
        assert match.condition_true is False

    def test_returns_none_for_non_state_change_event(self) -> None:
        event = QueueSnapshotEvent(
            event_id="e12",
            ts=_ts(),
            type="queue_snapshot",
            queue_id="billing",
            tickets_waiting=1,
            longest_wait_sec=10,
            sla_target_sec=60,
            agents_available=1,
            agents_on_call=0,
            volume_last_15m=1,
            volume_forecast_next_15m=1,
        )

        assert self.evaluator.evaluate(event, self.rule) is None
