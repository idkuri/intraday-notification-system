from __future__ import annotations

from datetime import UTC, datetime

from lib.schemas.enums import Audience, ChannelType, Severity, TriggerType
from lib.schemas.events import QueueSnapshotEvent
from lib.schemas.rules import RuleScope

from evaluator.rule_engine import RuleEngine
from tests.conftest import make_rule_read
from tests.evaluator.fake_notification_dedup_store import FakeNotificationDedupStore


def _queue_snapshot(
    *,
    queue_id: str = "billing",
    longest_wait_sec: int = 120,
    sla_target_sec: int = 60,
) -> QueueSnapshotEvent:
    return QueueSnapshotEvent(
        event_id="evt_sla_1",
        ts=datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        type="queue_snapshot",
        queue_id=queue_id,
        tickets_waiting=5,
        longest_wait_sec=longest_wait_sec,
        sla_target_sec=sla_target_sec,
        agents_available=2,
        agents_on_call=1,
        volume_last_15m=10,
        volume_forecast_next_15m=12,
    )


class TestRuleEngine:
    def setup_method(self) -> None:
        self.store = FakeNotificationDedupStore()
        self.engine = RuleEngine(self.store)

    def test_sla_breach_produces_one_notification_intent(self) -> None:
        rule = make_rule_read(
            id="rule_sla_billing",
            name="Billing SLA breach",
            audience=Audience.TEAM_LEAD,
            owner_id="lead_billing",
            scope=RuleScope(queue_ids=["billing"]),
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
            severity=Severity.CRITICAL,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        )
        event = _queue_snapshot()

        intents = self.engine.evaluate_event(event, [rule])

        assert len(intents) == 1
        intent = intents[0]
        assert intent.rule_id == rule.id
        assert intent.recipient_id == "lead_billing"
        assert intent.severity == Severity.CRITICAL
        assert intent.entity_key == "queue:billing"
        assert intent.triggering_event_id == event.event_id
        assert "SLA breached" in intent.title

    def test_scope_mismatch_produces_zero_intents(self) -> None:
        rule = make_rule_read(
            id="rule_sla_other",
            scope=RuleScope(queue_ids=["tier_2"]),
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
        )
        event = _queue_snapshot(queue_id="billing")

        intents = self.engine.evaluate_event(event, [rule])

        assert intents == []

    def test_disabled_rules_are_ignored(self) -> None:
        rule = make_rule_read(
            id="rule_disabled",
            enabled=False,
            scope=RuleScope(queue_ids=["billing"]),
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
        )
        event = _queue_snapshot()

        intents = self.engine.evaluate_event(event, [rule])

        assert intents == []
