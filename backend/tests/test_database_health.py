"""Tests for database connectivity checks."""

from datetime import UTC
from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from app.db.health import DatabaseHealthStatus, check_database_connection


def test_database_health_is_healthy_for_a_reachable_database() -> None:
    """A reachable database returns a UTC-stamped healthy result."""

    engine = create_engine("sqlite+pysqlite:///:memory:")
    try:
        result = check_database_connection(engine)
    finally:
        engine.dispose()

    assert result.status is DatabaseHealthStatus.HEALTHY
    assert result.is_healthy is True
    assert result.checked_at.tzinfo is UTC
    assert result.error_type is None


def test_database_health_does_not_expose_connection_errors() -> None:
    """Database failures are reported without leaking connection details."""

    engine = Mock(spec=Engine)
    engine.connect.side_effect = OperationalError(
        "SELECT 1",
        {},
        Exception("connection details must remain private"),
    )

    result = check_database_connection(engine)

    assert result.status is DatabaseHealthStatus.UNHEALTHY
    assert result.is_healthy is False
    assert result.error_type == "OperationalError"
