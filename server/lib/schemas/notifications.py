from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from lib.schemas.enums import ChannelType, Severity


class NotificationCreate(BaseModel):
    """Payload to create and deliver a notification (evaluator → notifier)."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(description="Rule that produced this notification.")
    recipient_id: str = Field(description="Who should receive the alert (usually rule owner).")
    title: str
    body: str
    severity: Severity
    entity_key: str = Field(
        description="Scoped entity, e.g. ``queue:billing`` or ``agent:a_19``.",
    )
    triggering_event_id: str
    ts: datetime
    channels: list[ChannelType]


class NotificationRead(BaseModel):
    """Persisted inbox notification."""

    model_config = ConfigDict(extra="forbid")

    id: str
    rule_id: str
    recipient_id: str
    title: str
    body: str
    severity: Severity
    entity_key: str
    triggering_event_id: str
    ts: datetime
    delivered_channels: list[ChannelType]
