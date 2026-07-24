from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IngestEventResponse(BaseModel):
    """Result of evaluating and delivering notifications for one ingested event.

    Attributes:
        notifications_emitted: Number of notifications created for this event.
        notification_ids: Primary keys of those notification rows, in creation order.
    """

    model_config = ConfigDict(extra="forbid")

    notifications_emitted: int = Field(description="Count of notifications created")
    notification_ids: list[str] = Field(description="IDs of created notification rows")
