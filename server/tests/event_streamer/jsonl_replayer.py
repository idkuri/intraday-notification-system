from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from pathlib import Path

import lib.models  # noqa: F401
from lib.schemas.events import Event, EventParser
from scripts.seed_rules import seed_rules_if_empty
from tests.event_streamer.streamer import EventStreamer
from tests.event_streamer.types import ReplayResult

from gateway.container import AppContainer
from ingest.ingest_service import IngestService


def _event_summary(event: Event) -> str:
    """Format a one-line human-readable summary for progress logging."""
    if event.type == "queue_snapshot":
        return (
            f"queue={event.queue_id} waiting={event.tickets_waiting} "
            f"longest_wait={event.longest_wait_sec}s sla={event.sla_target_sec}s"
        )
    if event.type == "agent_state_change":
        prev = event.previous_state if event.previous_state is not None else "none"
        if event.previous_state_duration_sec is None:
            duration = "n/a"
        else:
            duration = f"{event.previous_state_duration_sec}s"
        return f"agent={event.agent_id} {prev}->{event.new_state} (prev_duration={duration})"
    return (
        f"agent={event.agent_id} violation={event.in_violation} "
        f"scheduled={event.scheduled_state} actual={event.actual_state}"
    )


class JsonlReplayer:
    """Replay JSONL events through the ingest pipeline."""

    def __init__(
        self,
        ingest: IngestService,
        parser: EventParser,
        streamer: EventStreamer,
    ) -> None:
        self._ingest = ingest
        self._parser = parser
        self._streamer = streamer

    def run(
        self,
        path: str | Path,
        *,
        mode: str = "instant",
        stream_duration_sec: int = 600,
        reset: bool = True,
        on_event: Callable[[int, int, Event, int], None] | None = None,
    ) -> ReplayResult:
        """Replay events from a JSONL file and return aggregate statistics."""
        if reset:
            self._ingest.reset_state()
            self._ingest.session.commit()

        events = self._parser.parse_file(Path(path))
        total = len(events)

        if mode == "stream":
            event_iter = self._streamer.pace(events, stream_duration_sec=stream_duration_sec)
        else:
            event_iter = iter(events)

        notifications_sent = 0
        events_processed = 0
        start = time.monotonic()

        for event in event_iter:
            result = self._ingest.ingest_event(event)
            notifications_sent += result.notifications_emitted
            events_processed += 1
            self._ingest.session.commit()
            if on_event is not None:
                on_event(events_processed, total, event, result.notifications_emitted)

        wall_clock_sec = time.monotonic() - start
        return ReplayResult(
            events_processed=events_processed,
            notifications_sent=notifications_sent,
            wall_clock_sec=wall_clock_sec,
        )


def _print_progress(
    index: int,
    total: int,
    event: Event,
    emitted: int,
) -> None:
    elapsed = event.ts.isoformat().replace("+00:00", "Z")
    suffix = f" -> {emitted} notification(s)" if emitted else ""
    print(
        f"[EVENT] {index}/{total} {event.type} {event.event_id} @ {elapsed} "
        f"| {_event_summary(event)}{suffix}",
        flush=True,
    )


def main() -> None:
    """CLI entry point for replaying JSONL events."""
    parser = argparse.ArgumentParser(description="Replay JSONL events through the ingest pipeline")
    parser.add_argument("--events", default="events.jsonl", help="Path to JSONL event file")
    parser.add_argument(
        "--mode",
        choices=["instant", "stream"],
        default="instant",
        help="Replay pacing mode",
    )
    parser.add_argument(
        "--stream-duration-sec",
        type=int,
        default=600,
        help="Wall-clock duration for stream mode",
    )
    parser.add_argument("--db-url", default=None, help="Database URL override")
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Skip clearing notifications and notification-dedup before replay",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-event progress logs (notifications still print)",
    )
    args = parser.parse_args()

    db_url = args.db_url or "sqlite:///./data/assembled.db"
    container = AppContainer(db_url)
    container.db.create_all()

    session = container.session()
    try:
        seed_rules_if_empty(session)
        session.commit()

        ingest = container.ingest_service(session)
        replayer = JsonlReplayer(ingest, EventParser(), EventStreamer())

        events_path = Path(args.events)
        event_count = sum(1 for line in events_path.read_text().splitlines() if line.strip())
        if not args.quiet:
            if args.mode == "stream":
                print(
                    f"[REPLAY] Streaming {event_count} events over "
                    f"{args.stream_duration_sec}s wall clock from {events_path}",
                    flush=True,
                )
            else:
                print(
                    f"[REPLAY] Instant replay of {event_count} events from {events_path}",
                    flush=True,
                )

        result = replayer.run(
            args.events,
            mode=args.mode,
            stream_duration_sec=args.stream_duration_sec,
            reset=not args.no_reset,
            on_event=None if args.quiet else _print_progress,
        )
    finally:
        session.close()

    print(
        f"[REPLAY] Done - processed {result['events_processed']} events, "
        f"sent {result['notifications_sent']} notifications "
        f"in {result['wall_clock_sec']:.2f}s",
        flush=True,
        file=sys.stdout,
    )


if __name__ == "__main__":
    main()
