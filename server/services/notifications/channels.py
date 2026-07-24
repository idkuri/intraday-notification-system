from __future__ import annotations

from abc import ABC, abstractmethod

from lib.schemas.enums import ChannelType
from lib.schemas.notifications import NotificationCreate


class NotificationChannel(ABC):
    """Delivery backend for a single notification channel type."""

    @abstractmethod
    def deliver(self, data: NotificationCreate) -> ChannelType:
        """Send ``data`` through this channel.

        Returns:
            The channel type that handled delivery.
        """
        raise NotImplementedError


class ConsoleChannel(NotificationChannel):
    """Prints notifications to stdout for local development."""

    def deliver(self, data: NotificationCreate) -> ChannelType:
        """Log the notification as a single stdout line."""
        print(
            f"[NOTIFY] {data.severity.value} -> {data.recipient_id} | "
            f"{data.title} | {data.body}"
        )
        return ChannelType.CONSOLE
