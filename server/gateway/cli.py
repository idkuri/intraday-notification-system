"""Console entry points for local development and event streaming."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_dev() -> None:
    """Start the API with reload (console script: ``uv run dev``)."""
    import uvicorn

    uvicorn.run(
        "gateway.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


def _ensure_server_root_on_path() -> None:
    from pathlib import Path

    server_root = str(Path(__file__).resolve().parents[1])
    if server_root not in sys.path:
        sys.path.insert(0, server_root)


def run_seed_rules() -> None:
    """Seed demo rules (console script: ``uv run seed-rules``)."""
    _ensure_server_root_on_path()
    from scripts.seed_rules import main

    main()


def run_stream_events() -> None:
    """Stream sample JSONL events (console script: ``uv run stream-events``)."""
    _ensure_server_root_on_path()

    from tests.event_streamer.jsonl_replayer import main

    args = sys.argv[1:]
    if "--mode" not in args:
        args = ["--mode", "stream", "--stream-duration-sec", "600", *args]
    sys.argv = [sys.argv[0], *args]
    main()


def run_lint() -> None:
    """Run ruff check/format-check and mypy (console script: ``uv run lint``)."""
    server_root = Path(__file__).resolve().parents[1]
    targets = ["lib", "services", "gateway", "tests", "scripts"]
    commands = [
        ["ruff", "check", *targets],
        ["ruff", "format", "--check", *targets],
        ["mypy"],
    ]
    failed = False
    for cmd in commands:
        print(f"+ {' '.join(cmd)}", flush=True)
        result = subprocess.run(cmd, cwd=server_root, check=False)
        if result.returncode != 0:
            failed = True
    if failed:
        raise SystemExit(1)


def run_export_trigger_config() -> None:
    """Export trigger field config to the client (``uv run export-trigger-config``)."""
    _ensure_server_root_on_path()
    from scripts.export_trigger_field_config import main

    main()
