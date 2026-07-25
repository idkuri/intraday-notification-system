from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from lib.schemas.enums import AgentState, ChannelType, Severity, TriggerType


class RuleScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str | None = None
    queue_ids: list[str] | None = None


class RuleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    enabled: bool = True
    owner_id: str
    scope: RuleScope
    trigger_type: TriggerType
    threshold: int | None = None
    target_state: AgentState | None = None
    severity: Severity = Severity.WARNING
    channels: list[ChannelType] = Field(
        default_factory=lambda: [ChannelType.CONSOLE, ChannelType.INBOX]
    )


class RuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    enabled: bool | None = None
    owner_id: str | None = None
    scope: RuleScope | None = None
    trigger_type: TriggerType | None = None
    threshold: int | None = None
    target_state: AgentState | None = None
    severity: Severity | None = None
    channels: list[ChannelType] | None = None


class RuleRead(RuleCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str
