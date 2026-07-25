from __future__ import annotations

import time
from collections.abc import Callable, Iterator

from lib.schemas.events import Event


class EventStreamer:
    """Yield events with wall-clock delays proportional to their timestamps."""

    def __init__(self, sleep_fn: Callable[[float], None] = time.sleep) -> None:
        self._sleep_fn = sleep_fn

    def pace(self, events: list[Event], *, stream_duration_sec: int) -> Iterator[Event]:
        """Yield events spaced across ``stream_duration_sec`` of wall-clock time."""
        if not events:
            return iter([])

        t0 = events[0].ts
        span = max((events[-1].ts - t0).total_seconds(), 1.0)
        elapsed_sleep = 0.0

        for index, event in enumerate(events):
            if index > 0:
                target_wall = ((event.ts - t0).total_seconds() / span) * stream_duration_sec
                sleep_for = target_wall - elapsed_sleep
                if sleep_for > 0:
                    self._sleep_fn(sleep_for)
                    elapsed_sleep += sleep_for
            yield event
