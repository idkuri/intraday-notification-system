#!/usr/bin/env python3
"""Generate a deterministic sample intraday event feed (~100 events)."""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from lib.demo_roster import AGENT_IDS, AGENT_QUEUES, QUEUES
from lib.schemas.events import (
    AdherenceCheckEvent,
    AgentStateChangeEvent,
    Event,
    EventParser,
    QueueSnapshotEvent,
)

SEED = 42
START = datetime(2026, 5, 26, 13, 0, 0, tzinfo=UTC)
SPAN_MINUTES = 90
_PLACEHOLDER_EVENT_ID = ""

STATES = ["available", "on_call", "on_break", "in_meeting", "offline"]

OUTPUT_PATHS = [
    Path(__file__).resolve().parent.parent / "events.jsonl",
    Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "sample_events.jsonl",
]

_EVENT_PARSER = EventParser()


def ts_at(minute: float, second: int = 0) -> datetime:
    return START + timedelta(minutes=minute, seconds=second)


def _event_sort_key(event: Event) -> tuple[datetime, str, str]:
    if isinstance(event, QueueSnapshotEvent):
        scope_key = event.queue_id
    elif isinstance(event, AgentStateChangeEvent | AdherenceCheckEvent):
        scope_key = event.agent_id
    else:
        scope_key = ""
    return (event.ts, event.type, scope_key)


def queue_snapshot(
    ts: datetime,
    queue_id: str,
    *,
    tickets_waiting: int,
    longest_wait_sec: int,
    agents_available: int,
    agents_on_call: int,
    volume_last_15m: int,
    volume_forecast_next_15m: int,
) -> QueueSnapshotEvent:
    return QueueSnapshotEvent(
        event_id=_PLACEHOLDER_EVENT_ID,
        ts=ts,
        type="queue_snapshot",
        queue_id=queue_id,
        tickets_waiting=tickets_waiting,
        longest_wait_sec=longest_wait_sec,
        sla_target_sec=QUEUES[queue_id],
        agents_available=agents_available,
        agents_on_call=agents_on_call,
        volume_last_15m=volume_last_15m,
        volume_forecast_next_15m=volume_forecast_next_15m,
    )


def agent_state_change(
    ts: datetime,
    agent_id: str,
    *,
    previous_state: str,
    previous_state_duration_sec: int,
    new_state: str,
) -> AgentStateChangeEvent:
    return AgentStateChangeEvent(
        event_id=_PLACEHOLDER_EVENT_ID,
        ts=ts,
        type="agent_state_change",
        agent_id=agent_id,
        queue_ids=AGENT_QUEUES[agent_id],
        previous_state=previous_state,
        previous_state_duration_sec=previous_state_duration_sec,
        new_state=new_state,
    )


def adherence_check(
    ts: datetime,
    agent_id: str,
    *,
    scheduled_state: str,
    actual_state: str,
    in_violation: bool,
    violation_started_at: datetime | None,
) -> AdherenceCheckEvent:
    return AdherenceCheckEvent(
        event_id=_PLACEHOLDER_EVENT_ID,
        ts=ts,
        type="adherence_check",
        agent_id=agent_id,
        queue_ids=AGENT_QUEUES[agent_id],
        scheduled_state=scheduled_state,
        actual_state=actual_state,
        in_violation=in_violation,
        violation_started_at=violation_started_at,
    )


def story_events() -> list[Event]:
    """Curated beats that fire seed notification rules."""
    events: list[Event] = []
    violation_start = ts_at(10)

    # Billing backlog rising edge (below 20, then at/above 20).
    billing_backlog = [
        (2, 9, 38, 3, 2, 14, 16),
        (8, 14, 72, 2, 3, 18, 20),
        (14, 18, 98, 2, 4, 22, 24),
        (18, 22, 105, 1, 5, 26, 28),  # backlog threshold crossed
        (24, 26, 125, 1, 5, 28, 30),  # SLA threshold crossed
        (32, 24, 142, 2, 4, 24, 22),
        (40, 21, 118, 2, 3, 20, 19),
        (52, 17, 95, 3, 2, 17, 18),
    ]
    for minute, tickets, wait, avail, on_call, vol, forecast in billing_backlog:
        events.append(
            queue_snapshot(
                ts_at(minute, 15),
                "billing",
                tickets_waiting=tickets,
                longest_wait_sec=wait,
                agents_available=avail,
                agents_on_call=on_call,
                volume_last_15m=vol,
                volume_forecast_next_15m=forecast,
            )
        )

    # a_19 adherence violation crossing 600s with stable violation_started_at.
    for minute in (10, 15, 20, 25, 30, 35):
        events.append(
            adherence_check(
                ts_at(minute, 30),
                "a_19",
                scheduled_state="available",
                actual_state="on_break",
                in_violation=True,
                violation_started_at=violation_start,
            )
        )
    events.append(
        adherence_check(
            ts_at(42),
            "a_19",
            scheduled_state="available",
            actual_state="available",
            in_violation=False,
            violation_started_at=None,
        )
    )

    # a_42 long on_call ending after >= 2700s.
    events.append(
        agent_state_change(
            ts_at(48, 10),
            "a_42",
            previous_state="on_call",
            previous_state_duration_sec=2700,
            new_state="available",
        )
    )

    return events


def filler_events(rng: random.Random, count: int) -> list[Event]:
    events: list[Event] = []

    for _ in range(count):
        kind_roll = rng.random()
        minute = rng.uniform(0, SPAN_MINUTES)
        second = rng.randint(0, 59)
        ts = ts_at(minute, second)

        if kind_roll < 0.42:
            queue_id = rng.choice(list(QUEUES))
            if queue_id == "billing":
                tickets = rng.randint(4, 16)
                wait = rng.randint(20, 95)
            elif queue_id == "tier_2":
                tickets = rng.randint(2, 12)
                wait = rng.randint(30, 240)
            else:
                tickets = rng.randint(1, 8)
                wait = rng.randint(10, 50)

            events.append(
                queue_snapshot(
                    ts,
                    queue_id,
                    tickets_waiting=tickets,
                    longest_wait_sec=wait,
                    agents_available=rng.randint(1, 4),
                    agents_on_call=rng.randint(1, 5),
                    volume_last_15m=rng.randint(8, 30),
                    volume_forecast_next_15m=rng.randint(8, 32),
                )
            )
        elif kind_roll < 0.68:
            agent_id = rng.choice(AGENT_IDS)
            if agent_id == "a_42":
                continue
            prev = rng.choice(STATES)
            nxt = rng.choice([s for s in STATES if s != prev])
            events.append(
                agent_state_change(
                    ts,
                    agent_id,
                    previous_state=prev,
                    previous_state_duration_sec=rng.randint(120, 1800),
                    new_state=nxt,
                )
            )
        else:
            agent_id = rng.choice([a for a in AGENT_IDS if a != "a_19"])
            scheduled = rng.choice(["available", "on_call"])
            actual = scheduled if rng.random() < 0.82 else rng.choice(STATES)
            in_violation = actual != scheduled
            events.append(
                adherence_check(
                    ts,
                    agent_id,
                    scheduled_state=scheduled,
                    actual_state=actual,
                    in_violation=in_violation,
                    violation_started_at=ts if in_violation else None,
                )
            )

    return events


def assign_event_ids(events: list[Event]) -> list[Event]:
    events.sort(key=_event_sort_key)
    return [
        event.model_copy(update={"event_id": f"evt_{index:04d}"})
        for index, event in enumerate(events, start=1)
    ]


def generate_events() -> list[Event]:
    rng = random.Random(SEED)
    target_count = 95 + rng.randint(0, 15)

    story = story_events()
    filler: list[Event] = []
    while len(story) + len(filler) < target_count:
        filler.extend(filler_events(rng, 1))

    while len(story) + len(filler) > 110 and filler:
        filler.pop()

    while len(story) + len(filler) < 95:
        filler.extend(filler_events(rng, 1))

    return assign_event_ids(story + filler)


def main() -> None:
    events = generate_events()
    if not 95 <= len(events) <= 110:
        raise SystemExit(f"Expected 95-110 events, got {len(events)}")

    content = "\n".join(_EVENT_PARSER.dumps(event) for event in events) + "\n"
    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"Wrote {len(events)} events to:")
    for path in OUTPUT_PATHS:
        print(f"  {path}")


if __name__ == "__main__":
    main()
