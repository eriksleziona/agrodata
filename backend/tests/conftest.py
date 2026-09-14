"""Fixtures for backend domain tests."""

from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers all models with metadata
from app.core.security import create_access_token
from app.db.base import Base
from app.models.user import User


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Provide an isolated in-memory database session for each test."""

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    database_session = session_factory()
    try:
        yield database_session
    finally:
        database_session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def make_auth_headers(user: User) -> dict[str, str]:
    """Return a dict of HTTP headers carrying a valid JWT for *user*.

    Use this helper inside API test fixtures to authenticate requests:

        headers = make_auth_headers(user)
        client.get("/api/v1/machines", headers=headers)
    """

    token = create_access_token(
        user_id=user.id,
        organization_id=user.organization_id,
        role=user.role.value,
    )
    return {"Authorization": f"Bearer {token}"}
