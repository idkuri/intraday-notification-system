from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from lib.schemas.events import QueueSnapshotEvent
from tests.event_streamer.streamer import EventStreamer


def _snapshot(event_id: str, ts: datetime) -> QueueSnapshotEvent:
    return QueueSnapshotEvent(
        event_id=event_id,
        ts=ts,
        type="queue_snapshot",
        queue_id="billing",
        tickets_waiting=1,
        longest_wait_sec=10,
        sla_target_sec=60,
        agents_available=1,
        agents_on_call=0,
        volume_last_15m=1,
        volume_forecast_next_15m=1,
    )


class TestEventStreamer:
    def test_pace_records_sleeps_for_spread_events(self) -> None:
        t0 = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)
        events = [
            _snapshot("e1", t0),
            _snapshot("e2", t0 + timedelta(minutes=30)),
            _snapshot("e3", t0 + timedelta(minutes=90)),
        ]
        sleeps: list[float] = []

        streamer = EventStreamer(sleep_fn=sleeps.append)
        streamed = list(streamer.pace(events, stream_duration_sec=600))

        assert streamed == events
        assert len(sleeps) == 2
        assert sleeps[0] == pytest.approx(200.0, rel=1e-6)
        assert sleeps[1] == pytest.approx(400.0, rel=1e-6)
        assert sum(sleeps) == pytest.approx(600.0, rel=1e-6)

    def test_empty_events_yields_nothing(self) -> None:
        sleeps: list[float] = []
        streamer = EventStreamer(sleep_fn=sleeps.append)

        assert list(streamer.pace([], stream_duration_sec=600)) == []
        assert sleeps == []
