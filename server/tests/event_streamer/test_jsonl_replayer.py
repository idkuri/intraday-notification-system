from __future__ import annotations

from pathlib import Path

from gateway.container import AppContainer
from lib.schemas.events import EventParser
from tests.event_streamer.jsonl_replayer import JsonlReplayer
from tests.event_streamer.streamer import EventStreamer

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "sample_events.jsonl"


def _fixture_event_count() -> int:
    return sum(1 for line in FIXTURE_PATH.read_text().splitlines() if line.strip())


class TestJsonlReplayerIntegration:
    def test_instant_replay_processes_fixture_and_fires_notifications(
        self,
        app_container: AppContainer,
    ) -> None:
        expected_events = _fixture_event_count()
        assert expected_events == 98

        session = app_container.session()
        try:
            ingest = app_container.ingest_service(session)
            replayer = JsonlReplayer(ingest, EventParser(), EventStreamer())

            result = replayer.run(FIXTURE_PATH, mode="instant", reset=True)
        finally:
            session.close()

        assert result["events_processed"] == expected_events
        assert result["notifications_sent"] >= 4
