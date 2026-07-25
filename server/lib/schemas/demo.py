from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DemoAgentRead(BaseModel):
    """Agent in the demo workforce roster."""

    model_config = ConfigDict(extra="forbid")

    agent_id: str
    agent_name: str
    queue_ids: list[str]


class DemoRosterResponse(BaseModel):
    """Agents and queues used by the sample feed and rule UI pickers."""

    model_config = ConfigDict(extra="forbid")

    agents: list[DemoAgentRead]
    queues: list[str] = Field(description="Queue IDs present in the demo feed")
