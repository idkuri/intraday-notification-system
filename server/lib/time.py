"""Shared clock helpers (indirection helps freezegun in tests)."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)
