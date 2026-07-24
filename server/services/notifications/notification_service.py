from __future__ import annotations

from lib.models.notification import NotificationModel
from lib.models.notification_dedup import NotificationDedupModel
from lib.schemas.enums import ChannelType
from lib.schemas.notifications import NotificationCreate, NotificationRead
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from notifications.channels import ConsoleChannel, NotificationChannel


class NotificationService:
    """Persists notifications and delivers them via configured channels."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._channels: dict[ChannelType, NotificationChannel] = {
            ChannelType.CONSOLE: ConsoleChannel(),
        }

    def record_and_deliver(self, data: NotificationCreate) -> NotificationRead:
        """Deliver ``data`` through its channels and persist the notification record.

        Returns:
            The stored notification, including assigned ID and delivery metadata.
        """
        for channel_type in data.channels:
            if channel_type == ChannelType.CONSOLE:
                self._channels[ChannelType.CONSOLE].deliver(data)

        notification = NotificationModel.from_create(data, delivered_channels=list(data.channels))
        self._session.add(notification)
        self._session.flush()
        return notification.to_schema()

    def list_notifications(self) -> list[NotificationRead]:
        """Return all notifications, newest first."""
        notifications = self._session.scalars(
            select(NotificationModel).order_by(NotificationModel.ts.desc())
        ).all()
        return [notification.to_schema() for notification in notifications]

    def clear_all(self) -> None:
        """Delete every persisted notification."""
        self._session.execute(delete(NotificationModel))

    def clear_notification_dedup(self) -> None:
        """Delete RuleEngine prior-condition / window memory rows."""
        self._session.execute(delete(NotificationDedupModel))
