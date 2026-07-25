from __future__ import annotations

from typing import TypedDict


class ReplayResult(TypedDict):
    """Summary statistics from a JSONL replay run."""

    events_processed: int
    notifications_sent: int
    wall_clock_sec: float
