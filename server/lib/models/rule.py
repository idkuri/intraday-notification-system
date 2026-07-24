from __future__ import annotations

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.db.base import Base
from lib.schemas.enums import (
    AgentState,
    Audience,
    ChannelType,
    Severity,
    TriggerType,
)
from lib.schemas.rules import RuleCreate, RuleRead, RuleScope, RuleUpdate
from lib.time import utc_now

if TYPE_CHECKING:
    from lib.models.notification import NotificationModel
    from lib.models.notification_dedup import NotificationDedupModel

_UNSET: Any = object()
_ENUM_UPDATE_FIELDS = frozenset({"audience", "trigger_type", "target_state", "severity"})
_PLAIN_UPDATE_FIELDS = frozenset({"name", "enabled", "owner_id", "threshold"})


def _enum_value(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


class RuleModel(Base):
    """ORM row for a configured notification rule."""

    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    audience: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    scope_agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    scope_queue_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(64), nullable=False)
    threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    channels_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False)

    notifications: Mapped[list[NotificationModel]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    notification_dedups: Mapped[list[NotificationDedupModel]] = relationship(
        back_populates="rule",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_schema(self) -> RuleRead:
        """Convert this row to a ``RuleRead`` schema."""
        queue_ids: list[str] | None = None
        if self.scope_queue_ids_json is not None:
            raw = json.loads(self.scope_queue_ids_json)
            queue_ids = list(raw) if raw is not None else None
        channels = [ChannelType(c) for c in json.loads(self.channels_json)]
        return RuleRead(
            id=self.id,
            name=self.name,
            enabled=self.enabled,
            audience=Audience(self.audience),
            owner_id=self.owner_id,
            scope=RuleScope(agent_id=self.scope_agent_id, queue_ids=queue_ids),
            trigger_type=TriggerType(self.trigger_type),
            threshold=self.threshold,
            target_state=AgentState(self.target_state) if self.target_state else None,
            severity=Severity(self.severity),
            channels=channels,
            created_at=self.created_at,
            updated_at=self.updated_at,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )

    @classmethod
    def from_create(cls, data: RuleCreate, *, actor: str, rule_id: str | None = None) -> RuleModel:
        """Alternate constructor: build a new rule row from a create payload."""
        now = utc_now()
        queue_ids_json: str | None = None
        if data.scope.queue_ids is not None:
            queue_ids_json = json.dumps(data.scope.queue_ids)
        return cls(
            id=rule_id or f"rule_{uuid.uuid4().hex[:12]}",
            name=data.name,
            enabled=data.enabled,
            audience=data.audience.value,
            owner_id=data.owner_id,
            scope_agent_id=data.scope.agent_id,
            scope_queue_ids_json=queue_ids_json,
            trigger_type=data.trigger_type.value,
            threshold=data.threshold,
            target_state=data.target_state.value if data.target_state else None,
            severity=data.severity.value,
            channels_json=json.dumps([c.value for c in data.channels]),
            created_at=now,
            updated_at=now,
            created_by=actor,
            updated_by=actor,
        )

    def apply_update(self, data: RuleUpdate, *, actor: str) -> None:
        """Apply a partial ``RuleUpdate`` to this row (only fields present in the payload)."""
        patch = data.model_dump(exclude_unset=True)
        scope = patch.pop("scope", _UNSET)
        channels = patch.pop("channels", _UNSET)

        for key, value in patch.items():
            if value is None:
                continue
            if key in _ENUM_UPDATE_FIELDS:
                setattr(self, key, _enum_value(value))
            elif key in _PLAIN_UPDATE_FIELDS:
                setattr(self, key, value)

        if scope is not _UNSET and scope is not None:
            self.scope_agent_id = scope.get("agent_id")
            queue_ids = scope.get("queue_ids")
            self.scope_queue_ids_json = json.dumps(queue_ids) if queue_ids is not None else None

        if channels is not _UNSET and channels is not None:
            self.channels_json = json.dumps([_enum_value(c) for c in channels])

        self.updated_at = utc_now()
        self.updated_by = actor
