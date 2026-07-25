from __future__ import annotations

from datetime import UTC, datetime, timedelta

from lib.schemas.enums import TriggerType
from lib.schemas.events import (
    AdherenceCheckEvent,
    AgentStateChangeEvent,
    QueueSnapshotEvent,
)
from lib.schemas.rules import RuleScope

from evaluator.rule_engine import RuleEngine
from tests.conftest import make_rule_read
from tests.evaluator.fake_notification_dedup_store import FakeNotificationDedupStore


def _ts(offset_sec: int = 0) -> datetime:
    return datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=offset_sec)


def _sla_snapshot(*, longest_wait_sec: int, event_id: str, offset_sec: int) -> QueueSnapshotEvent:
    return QueueSnapshotEvent(
        event_id=event_id,
        ts=_ts(offset_sec),
        type="queue_snapshot",
        queue_id="billing",
        tickets_waiting=5,
        longest_wait_sec=longest_wait_sec,
        sla_target_sec=60,
        agents_available=2,
        agents_on_call=1,
        volume_last_15m=10,
        volume_forecast_next_15m=12,
    )


class TestRuleEngineNoiseControl:
    def setup_method(self) -> None:
        self.store = FakeNotificationDedupStore()
        self.engine = RuleEngine(self.store)

    def test_become_true_first_allows_second_consecutive_true_denies(self) -> None:
        rule = make_rule_read(
            id="rule_sla",
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
        )
        first = _sla_snapshot(longest_wait_sec=120, event_id="evt_1", offset_sec=0)
        second = _sla_snapshot(longest_wait_sec=120, event_id="evt_2", offset_sec=60)

        assert len(self.engine.evaluate_event(first, [rule])) == 1
        assert self.engine.evaluate_event(second, [rule]) == []

    def test_condition_false_resets_then_true_allows_again(self) -> None:
        rule = make_rule_read(
            id="rule_sla",
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
        )
        breached = _sla_snapshot(longest_wait_sec=120, event_id="evt_1", offset_sec=0)
        still = _sla_snapshot(longest_wait_sec=120, event_id="evt_2", offset_sec=60)
        recovered = _sla_snapshot(longest_wait_sec=30, event_id="evt_3", offset_sec=120)
        breached_again = _sla_snapshot(longest_wait_sec=120, event_id="evt_4", offset_sec=180)

        assert len(self.engine.evaluate_event(breached, [rule])) == 1
        assert self.engine.evaluate_event(still, [rule]) == []
        assert self.engine.evaluate_event(recovered, [rule]) == []
        assert len(self.engine.evaluate_event(breached_again, [rule])) == 1

    def test_adherence_same_violation_window_denies_second_fire(self) -> None:
        rule = make_rule_read(
            id="rule_adherence",
            trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
            scope=RuleScope(agent_id="a_19"),
            threshold=600,
        )
        window_start = datetime(2026, 1, 15, 11, 50, 0, tzinfo=UTC)
        first = AdherenceCheckEvent(
            event_id="evt_adh_1",
            ts=_ts(600),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="in_meeting",
            in_violation=True,
            violation_started_at=window_start,
        )
        cleared = AdherenceCheckEvent(
            event_id="evt_adh_2",
            ts=_ts(700),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="available",
            in_violation=False,
            violation_started_at=None,
        )
        same_window = AdherenceCheckEvent(
            event_id="evt_adh_3",
            ts=_ts(800),
            type="adherence_check",
            agent_id="a_19",
            queue_ids=["billing"],
            scheduled_state="available",
            actual_state="in_meeting",
            in_violation=True,
            violation_started_at=window_start,
        )

        assert len(self.engine.evaluate_event(first, [rule])) == 1
        assert self.engine.evaluate_event(cleared, [rule]) == []
        assert self.engine.evaluate_event(same_window, [rule]) == []

    def test_agent_state_duration_allows_each_true_match(self) -> None:
        rule = make_rule_read(
            id="rule_state",
            trigger_type=TriggerType.AGENT_STATE_DURATION,
            scope=RuleScope(agent_id="a_42"),
            threshold=2700,
            target_state="on_call",
        )
        first = AgentStateChangeEvent(
            event_id="evt_state_1",
            ts=_ts(0),
            type="agent_state_change",
            agent_id="a_42",
            queue_ids=["billing"],
            previous_state="on_call",
            previous_state_duration_sec=2700,
            new_state="on_break",
        )
        second = AgentStateChangeEvent(
            event_id="evt_state_2",
            ts=_ts(60),
            type="agent_state_change",
            agent_id="a_42",
            queue_ids=["billing"],
            previous_state="on_call",
            previous_state_duration_sec=2800,
            new_state="available",
        )

        assert len(self.engine.evaluate_event(first, [rule])) == 1
        assert len(self.engine.evaluate_event(second, [rule])) == 1
