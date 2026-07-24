from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.db.base import Base
from lib.schemas.enums import ChannelType, Severity
from lib.schemas.notifications import NotificationCreate, NotificationRead

if TYPE_CHECKING:
    from lib.models.rule import RuleModel


class NotificationModel(Base):
    """ORM row for a delivered inbox notification."""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    rule_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_key: Mapped[str] = mapped_column(String(128), nullable=False)
    triggering_event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered_channels_json: Mapped[str] = mapped_column(Text, nullable=False)

    rule: Mapped[RuleModel] = relationship(back_populates="notifications")

    def to_schema(self) -> NotificationRead:
        """Convert this row to a ``NotificationRead`` schema."""
        return NotificationRead(
            id=self.id,
            rule_id=self.rule_id,
            recipient_id=self.recipient_id,
            title=self.title,
            body=self.body,
            severity=Severity(self.severity),
            entity_key=self.entity_key,
            triggering_event_id=self.triggering_event_id,
            ts=self.ts,
            delivered_channels=[ChannelType(c) for c in json.loads(self.delivered_channels_json)],
        )

    @classmethod
    def from_create(
        cls,
        data: NotificationCreate,
        *,
        delivered_channels: list[ChannelType],
        notification_id: str | None = None,
    ) -> NotificationModel:
        """Alternate constructor: build a persisted notification from a create payload."""
        return cls(
            id=notification_id or f"notif_{uuid.uuid4().hex[:12]}",
            rule_id=data.rule_id,
            recipient_id=data.recipient_id,
            title=data.title,
            body=data.body,
            severity=data.severity.value,
            entity_key=data.entity_key,
            triggering_event_id=data.triggering_event_id,
            ts=data.ts,
            delivered_channels_json=json.dumps([c.value for c in delivered_channels]),
        )
