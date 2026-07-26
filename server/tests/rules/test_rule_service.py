from __future__ import annotations

import pytest
from lib.exceptions import DomainValidationError, NotFoundError
from lib.models.notification_dedup import NotificationDedupModel
from lib.schemas.enums import AgentState, ChannelType, Severity, TriggerType
from lib.schemas.notification_dedup import NotificationDedupCreate
from lib.schemas.rules import RuleCreate, RuleScope, RuleUpdate
from scripts.seed_rules import seed_rules_if_empty
from sqlalchemy import select

from rules.rule_service import RuleService


def _agent_rule(*, name: str, owner_id: str = "a_1") -> RuleCreate:
    return RuleCreate(
        name=name,
        owner_id=owner_id,
        scope=RuleScope(agent_id=owner_id),
        trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
        threshold=600,
    )


class TestRuleService:
    def test_create_get_update_delete(self, db_session) -> None:
        service = RuleService(db_session)
        created = service.create_rule(
            RuleCreate(
                name="Billing SLA breach",
                owner_id="lead_billing",
                scope=RuleScope(queue_ids=["billing"]),
                trigger_type=TriggerType.QUEUE_SLA_BREACHED,
                severity=Severity.CRITICAL,
                channels=[ChannelType.CONSOLE, ChannelType.INBOX],
            ),
            actor="tester",
        )

        assert created.id.startswith("rule_")
        assert created.created_by == "tester"
        assert created.updated_by == "tester"
        assert created.owner_id == "tester"

        fetched = service.get_rule(created.id, actor="tester")
        assert fetched is not None
        assert fetched.name == "Billing SLA breach"

        updated = service.update_rule(
            created.id,
            RuleUpdate(name="Updated SLA rule"),
            actor="tester",
        )
        assert updated.name == "Updated SLA rule"
        assert updated.updated_by == "tester"

        service.delete_rule(created.id, actor="tester")
        db_session.flush()
        assert service.get_rule(created.id, actor="tester") is None
        with pytest.raises(NotFoundError):
            service.require_rule(created.id, actor="tester")

    def test_update_rule_clears_dedup_rows(self, db_session) -> None:
        service = RuleService(db_session)
        created = service.create_rule(
            RuleCreate(
                name="Billing backlog",
                owner_id="lead_billing",
                scope=RuleScope(queue_ids=["billing"]),
                trigger_type=TriggerType.QUEUE_TICKETS_WAITING,
                threshold=20,
            ),
            actor="tester",
        )
        db_session.add(
            NotificationDedupModel.from_create(
                NotificationDedupCreate(
                    rule_id=created.id,
                    entity_key="queue:billing",
                    last_condition_true=True,
                )
            )
        )
        db_session.flush()

        service.update_rule(created.id, RuleUpdate(threshold=15), actor="tester")
        db_session.flush()

        remaining = db_session.scalars(
            select(NotificationDedupModel).where(NotificationDedupModel.rule_id == created.id)
        ).all()
        assert remaining == []

    def test_list_rules_scoped_to_actor(self, db_session) -> None:
        service = RuleService(db_session)
        service.create_rule(_agent_rule(name="Alice rule"), actor="alice")
        service.create_rule(_agent_rule(name="Bob rule", owner_id="a_2"), actor="bob")

        alice_rules = service.list_rules(actor="alice")
        bob_rules = service.list_rules(actor="bob")

        assert [rule.name for rule in alice_rules] == ["Alice rule"]
        assert alice_rules[0].owner_id == "alice"
        assert [rule.name for rule in bob_rules] == ["Bob rule"]
        assert bob_rules[0].owner_id == "bob"

    def test_list_enabled_rules_is_global(self, db_session) -> None:
        service = RuleService(db_session)
        service.create_rule(_agent_rule(name="Enabled rule"), actor="alice")
        disabled = service.create_rule(
            RuleCreate(
                name="Disabled rule",
                enabled=False,
                owner_id="a_2",
                scope=RuleScope(agent_id="a_2"),
                trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
                threshold=600,
            ),
            actor="bob",
        )

        enabled_rules = service.list_enabled_rules()

        assert len(enabled_rules) == 1
        assert enabled_rules[0].name == "Enabled rule"
        assert disabled.enabled is False

    def test_cross_user_get_update_delete_not_found(self, db_session) -> None:
        service = RuleService(db_session)
        created = service.create_rule(_agent_rule(name="Alice rule"), actor="alice")

        assert service.get_rule(created.id, actor="bob") is None
        with pytest.raises(NotFoundError):
            service.require_rule(created.id, actor="bob")
        with pytest.raises(NotFoundError):
            service.update_rule(created.id, RuleUpdate(name="Hijacked"), actor="bob")
        with pytest.raises(NotFoundError):
            service.delete_rule(created.id, actor="bob")

        still_there = service.require_rule(created.id, actor="alice")
        assert still_there.name == "Alice rule"

    @pytest.mark.parametrize(
        ("payload", "message_fragment"),
        [
            (
                RuleCreate(
                    name="",
                    owner_id="lead",
                    scope=RuleScope(queue_ids=["billing"]),
                    trigger_type=TriggerType.QUEUE_SLA_BREACHED,
                ),
                "name must be non-empty",
            ),
            (
                RuleCreate(
                    name="Bad tickets rule",
                    owner_id="lead",
                    scope=RuleScope(queue_ids=["billing"]),
                    trigger_type=TriggerType.QUEUE_TICKETS_WAITING,
                    threshold=0,
                ),
                "threshold must be > 0",
            ),
            (
                RuleCreate(
                    name="Bad forecast-over-volume rule",
                    owner_id="lead",
                    scope=RuleScope(queue_ids=["billing"]),
                    trigger_type=TriggerType.QUEUE_FORECAST_OVER_VOLUME,
                    threshold=None,
                ),
                "threshold must be > 0",
            ),
            (
                RuleCreate(
                    name="Bad adherence rule",
                    owner_id="a_1",
                    scope=RuleScope(agent_id=""),
                    trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
                    threshold=600,
                ),
                "scope.agent_id is required",
            ),
            (
                RuleCreate(
                    name="Bad state rule",
                    owner_id="a_1",
                    scope=RuleScope(agent_id="a_1"),
                    trigger_type=TriggerType.AGENT_STATE_DURATION,
                    threshold=600,
                    target_state=None,
                ),
                "target_state is required",
            ),
            (
                RuleCreate(
                    name="Bad state scope rule",
                    owner_id="a_1",
                    scope=RuleScope(),
                    trigger_type=TriggerType.AGENT_STATE_DURATION,
                    threshold=600,
                    target_state=AgentState.ON_CALL,
                ),
                "scope.agent_id and/or scope.queue_ids is required",
            ),
        ],
    )
    def test_validation_errors_raise_domain_validation_error(
        self, db_session, payload: RuleCreate, message_fragment: str
    ) -> None:
        service = RuleService(db_session)

        with pytest.raises(DomainValidationError, match=message_fragment):
            service.create_rule(payload, actor="tester")

    def test_empty_actor_raises(self, db_session) -> None:
        service = RuleService(db_session)
        payload = RuleCreate(
            name="Valid rule",
            owner_id="lead",
            scope=RuleScope(queue_ids=["billing"]),
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
        )

        with pytest.raises(DomainValidationError, match="actor must be non-empty"):
            service.create_rule(payload, actor="  ")


class TestSeedRulesScript:
    def test_seed_rules_if_empty_creates_six_rules(self, db_session) -> None:
        inserted = seed_rules_if_empty(db_session)
        db_session.flush()

        service = RuleService(db_session)
        all_enabled = service.list_enabled_rules()

        assert inserted == 6
        assert len(all_enabled) == 6
        assert {rule.id for rule in all_enabled} == {
            "rule_agent_adherence",
            "rule_lead_sla_billing",
            "rule_lead_tickets_billing",
            "rule_lead_forecast_over_volume",
            "rule_lead_long_call",
            "rule_agent_long_call",
        }

    def test_seed_rules_scoped_by_demo_persona(self, db_session) -> None:
        seed_rules_if_empty(db_session)
        db_session.flush()

        service = RuleService(db_session)
        lead_rules = service.list_rules(actor="lead_billing")
        a19_rules = service.list_rules(actor="a_19")
        a42_rules = service.list_rules(actor="a_42")

        assert {rule.id for rule in lead_rules} == {
            "rule_lead_sla_billing",
            "rule_lead_tickets_billing",
            "rule_lead_forecast_over_volume",
            "rule_lead_long_call",
        }
        assert {rule.id for rule in a19_rules} == {"rule_agent_adherence"}
        assert {rule.id for rule in a42_rules} == {"rule_agent_long_call"}
        assert service.list_rules(actor="system") == []

    def test_seed_rules_if_empty_is_idempotent(self, db_session) -> None:
        assert seed_rules_if_empty(db_session) == 6
        assert seed_rules_if_empty(db_session) == 0

        service = RuleService(db_session)
        assert len(service.list_enabled_rules()) == 6
