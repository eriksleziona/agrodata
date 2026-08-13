"""Database connectivity health checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.time import utc_now


class DatabaseHealthStatus(StrEnum):
    """The possible database connectivity states."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True, slots=True)
class DatabaseHealth:
    """A non-sensitive result of a database connectivity check."""

    status: DatabaseHealthStatus
    checked_at: datetime
    error_type: str | None = None

    @property
    def is_healthy(self) -> bool:
        """Return whether the database was reachable."""

        return self.status is DatabaseHealthStatus.HEALTHY


def check_database_connection(engine: Engine) -> DatabaseHealth:
    """Check that a database connection can execute a lightweight query.

    Errors are reduced to their exception class name so API health responses do
    not expose connection URLs, credentials, or database internals.
    """

    checked_at = utc_now()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        return DatabaseHealth(
            status=DatabaseHealthStatus.UNHEALTHY,
            checked_at=checked_at,
            error_type=type(error).__name__,
        )

    return DatabaseHealth(
        status=DatabaseHealthStatus.HEALTHY,
        checked_at=checked_at,
    )
