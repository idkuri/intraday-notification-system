#!/usr/bin/env python3
"""Keep the test fixture identical to the canonical demo feed.

``events.jsonl`` is the source of truth (provided sample morning). This script
copies it to ``tests/fixtures/sample_events.jsonl`` so demos and tests stay in
sync. It does not synthesize a new feed.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from lib.schemas.events import EventParser

SERVER_ROOT = Path(__file__).resolve().parent.parent
CANONICAL = SERVER_ROOT / "events.jsonl"
FIXTURE = SERVER_ROOT / "tests" / "fixtures" / "sample_events.jsonl"


def main() -> None:
    if not CANONICAL.is_file():
        raise SystemExit(f"Missing canonical feed: {CANONICAL}")

    parser = EventParser()
    lines = [line for line in CANONICAL.read_text(encoding="utf-8").splitlines() if line.strip()]
    for index, line in enumerate(lines, start=1):
        try:
            parser.parse_line(line)
        except Exception as exc:  # noqa: BLE001 - surface line number for bad feed rows
            raise SystemExit(f"Invalid event on line {index}: {exc}") from exc

    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CANONICAL, FIXTURE)

    print(f"Synced {len(lines)} events:")
    print(f"  {CANONICAL}")
    print(f"  -> {FIXTURE}")


if __name__ == "__main__":
    main()
