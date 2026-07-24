from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NotificationDedupCreate(BaseModel):
    """Insert prior-condition memory for ``(rule_id, entity_key)``."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(description="Rule this row belongs to.")
    entity_key: str = Field(
        description="Scoped entity, e.g. ``queue:billing`` or ``agent:a_19``.",
    )
    last_condition_true: bool = Field(
        default=False,
        description="Whether the trigger condition was true on the previous evaluation.",
    )
    last_violation_window_id: str | None = Field(
        default=None,
        description="Adherence window id already notified for; suppresses duplicate fires.",
    )


class NotificationDedupUpdate(BaseModel):
    """Partial update for notification-dedup fields."""

    model_config = ConfigDict(extra="forbid")

    last_condition_true: bool | None = None
    last_violation_window_id: str | None = None


class NotificationDedupRead(NotificationDedupCreate):
    """Prior condition/window for one ``(rule_id, entity_key)``.

    Used by ``RuleEngine`` so snapshot feeds notify when a condition becomes
    true, not on every later poll while it stays true.
    """
