"""Demo workforce roster for sample feeds and the ``/demo/roster`` API.

Single source of truth for agent IDs, display names, and queue memberships.
Also consumed by ``scripts/generate_events.py``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DemoAgent:
    agent_id: str
    agent_name: str
    queue_ids: tuple[str, ...]


# Queue id -> SLA target seconds (matches sample event generator).
QUEUES: dict[str, int] = {
    "billing": 120,
    "tier_2": 300,
    "vip": 60,
}

AGENTS: tuple[DemoAgent, ...] = (
    DemoAgent("a_11", "Jordan Lee", ("billing",)),
    DemoAgent("a_19", "Avery Chen", ("billing", "tier_2")),
    DemoAgent("a_22", "Sam Rivera", ("tier_2",)),
    DemoAgent("a_31", "Casey Nguyen", ("vip",)),
    DemoAgent("a_42", "Riley Park", ("billing", "tier_2", "vip")),
    DemoAgent("a_55", "Morgan Blake", ("billing", "vip")),
    DemoAgent("a_61", "Quinn Harper", ("tier_2", "vip")),
    DemoAgent("a_77", "Jamie Ortiz", ("billing",)),
)

AGENT_IDS: tuple[str, ...] = tuple(agent.agent_id for agent in AGENTS)

AGENT_QUEUES: dict[str, list[str]] = {agent.agent_id: list(agent.queue_ids) for agent in AGENTS}
