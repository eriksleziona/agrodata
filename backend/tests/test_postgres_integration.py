"""Optional PostgreSQL/PostGIS connectivity integration test."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text

from app.db.health import check_database_connection


@pytest.mark.integration
def test_postgresql_and_postgis_are_available() -> None:
    """Verify the configured PostgreSQL database accepts PostGIS queries."""

    database_url = os.getenv("AGRODATA_TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("AGRODATA_TEST_DATABASE_URL is not configured")

    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        health = check_database_connection(engine)
        with engine.connect() as connection:
            postgis_enabled = connection.scalar(
                text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM pg_extension WHERE extname = 'postgis'"
                    ")"
                )
            )
    finally:
        engine.dispose()

    assert health.is_healthy is True
    assert postgis_enabled is True
