"""Insert demo default rules into an empty database.

Usage (from server/):

    uv run seed-rules
    # or: uv run python scripts/seed_rules.py
"""

from __future__ import annotations

import argparse

import lib.models  # noqa: F401
from gateway.container import AppContainer
from lib.models.rule import RuleModel
from lib.schemas.enums import AgentState, Audience, ChannelType, Severity, TriggerType
from lib.schemas.rules import RuleCreate, RuleScope
from sqlalchemy import func, select
from sqlalchemy.orm import Session

_SEED_RULES: list[tuple[str, RuleCreate]] = [
    (
        "rule_agent_adherence",
        RuleCreate(
            name="My adherence > 10m",
            audience=Audience.AGENT,
            owner_id="a_19",
            scope=RuleScope(agent_id="a_19"),
            trigger_type=TriggerType.ADHERENCE_VIOLATION_DURATION,
            threshold=600,
            severity=Severity.WARNING,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        ),
    ),
    (
        "rule_lead_sla_billing",
        RuleCreate(
            name="Billing SLA breach",
            audience=Audience.TEAM_LEAD,
            owner_id="lead_billing",
            scope=RuleScope(queue_ids=["billing"]),
            trigger_type=TriggerType.QUEUE_SLA_BREACHED,
            severity=Severity.CRITICAL,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        ),
    ),
    (
        "rule_lead_tickets_billing",
        RuleCreate(
            name="Billing backlog ≥ 20",
            audience=Audience.TEAM_LEAD,
            owner_id="lead_billing",
            scope=RuleScope(queue_ids=["billing"]),
            trigger_type=TriggerType.QUEUE_TICKETS_WAITING,
            threshold=20,
            severity=Severity.WARNING,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        ),
    ),
    (
        "rule_lead_long_call",
        RuleCreate(
            name="Long call ≥ 45m",
            audience=Audience.TEAM_LEAD,
            owner_id="lead_billing",
            scope=RuleScope(queue_ids=["billing", "tier_2", "vip"]),
            trigger_type=TriggerType.AGENT_STATE_DURATION,
            threshold=2700,
            target_state=AgentState.ON_CALL,
            severity=Severity.WARNING,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        ),
    ),
    (
        "rule_agent_long_call",
        RuleCreate(
            name="My long call ≥ 45m",
            audience=Audience.AGENT,
            owner_id="a_42",
            scope=RuleScope(agent_id="a_42"),
            trigger_type=TriggerType.AGENT_STATE_DURATION,
            threshold=2700,
            target_state=AgentState.ON_CALL,
            severity=Severity.INFO,
            channels=[ChannelType.CONSOLE, ChannelType.INBOX],
        ),
    ),
]


def seed_rules_if_empty(session: Session) -> int:
    """Insert demo rules when none exist.

    Args:
        session: Open SQLAlchemy session (caller commits).

    Returns:
        Number of rules inserted (0 if the table was already non-empty).
    """
    count = session.scalar(select(func.count()).select_from(RuleModel))
    if count and count > 0:
        return 0

    for rule_id, data in _SEED_RULES:
        # created_by matches the demo persona so reviewers see seed rules
        # when they set X-Username to a_19 / a_42 / lead_billing.
        session.add(
            RuleModel.from_create(data, actor=data.owner_id, rule_id=rule_id)
        )
    session.flush()
    return len(_SEED_RULES)


def main() -> None:
    """CLI entry: create tables if needed and seed demo rules."""
    parser = argparse.ArgumentParser(description="Seed demo notification rules")
    parser.add_argument("--db-url", default=None, help="Database URL override")
    args = parser.parse_args()

    container = AppContainer(args.db_url or "sqlite:///./data/assembled.db")
    container.db.create_all()

    session = container.session()
    try:
        inserted = seed_rules_if_empty(session)
        session.commit()
    finally:
        session.close()

    if inserted:
        print(f"Seeded {inserted} demo rules.")
    else:
        print("Rules table already has data; nothing to seed.")


if __name__ == "__main__":
    main()
