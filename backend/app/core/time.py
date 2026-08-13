"""UTC time helpers for persistence and API boundaries."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return a timezone-aware current UTC timestamp."""

    return datetime.now(UTC)
