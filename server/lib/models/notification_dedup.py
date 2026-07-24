from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.db.base import Base
from lib.schemas.notification_dedup import (
    NotificationDedupCreate,
    NotificationDedupRead,
    NotificationDedupUpdate,
)

if TYPE_CHECKING:
    from lib.models.rule import RuleModel


class NotificationDedupModel(Base):
    """ORM row for prior condition/window memory (table ``notification_dedup``)."""

    __tablename__ = "notification_dedup"

    rule_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    entity_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    last_condition_true: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_violation_window_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    rule: Mapped[RuleModel] = relationship(back_populates="notification_dedups")

    def to_schema(self) -> NotificationDedupRead:
        """Convert this row to a ``NotificationDedupRead`` schema."""
        return NotificationDedupRead(
            rule_id=self.rule_id,
            entity_key=self.entity_key,
            last_condition_true=self.last_condition_true,
            last_violation_window_id=self.last_violation_window_id,
        )

    @classmethod
    def from_create(cls, data: NotificationDedupCreate) -> NotificationDedupModel:
        """Alternate constructor: build a new row from a create payload."""
        return cls(
            rule_id=data.rule_id,
            entity_key=data.entity_key,
            last_condition_true=data.last_condition_true,
            last_violation_window_id=data.last_violation_window_id,
        )

    def apply_update(self, data: NotificationDedupUpdate) -> None:
        """Apply a partial update; explicit ``None`` clears nullable fields."""
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(self, key, value)
