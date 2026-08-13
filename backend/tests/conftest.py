"""Fixtures for backend domain tests."""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.db.base import Base


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Provide an isolated in-memory database session for each test."""

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    database_session = session_factory()
    try:
        yield database_session
    finally:
        database_session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
