from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class QueueSnapshotEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    ts: datetime
    type: Literal["queue_snapshot"]
    queue_id: str
    tickets_waiting: int
    longest_wait_sec: int
    sla_target_sec: int
    agents_available: int
    agents_on_call: int
    volume_last_15m: int
    volume_forecast_next_15m: Optional[int] = None


class AgentStateChangeEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    ts: datetime
    type: Literal["agent_state_change"]
    agent_id: str
    queue_ids: Optional[list[str]] = None
    previous_state: Optional[str] = None
    previous_state_duration_sec: Optional[int] = None
    new_state: str


class AdherenceCheckEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    ts: datetime
    type: Literal["adherence_check"]
    agent_id: str
    queue_ids: Optional[list[str]] = None
    scheduled_state: str
    actual_state: str
    in_violation: bool
    violation_started_at: Optional[datetime] = None


Event = Annotated[
    QueueSnapshotEvent | AgentStateChangeEvent | AdherenceCheckEvent,
    Field(discriminator="type"),
]

_event_adapter: TypeAdapter[Event] = TypeAdapter(Event)


class EventParser:
    """Parse and serialize discriminated domain events from JSON."""

    def parse_line(self, line: str) -> Event:
        """Parse a single JSONL line into a validated event."""
        return _event_adapter.validate_json(line)

    def parse_file(self, path: Path) -> list[Event]:
        """Parse all non-empty lines from a JSONL file, sorted by timestamp."""
        events: list[Event] = []
        with path.open(encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line:
                    continue
                events.append(self.parse_line(line))
        events.sort(key=lambda e: (e.ts, e.event_id))
        return events

    def parse_obj(self, data: Mapping[str, Any]) -> Event:
        """Validate a parsed JSON object into a discriminated event."""
        return _event_adapter.validate_python(data)

    def dumps(self, event: Event) -> str:
        """Serialize an event to a JSON string."""
        return json.dumps(event.model_dump(mode="json"))
