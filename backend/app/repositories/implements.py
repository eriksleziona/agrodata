"""Implement persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.implement import Implement


class ImplementRepository:
    """Database access operations for agricultural implements."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, implement: Implement) -> Implement:
        """Add an implement to the current unit of work."""

        self._session.add(implement)
        return implement

    def get_by_id(self, implement_id: UUID) -> Implement | None:
        """Return an implement by its UUID, if it exists."""

        return self._session.get(Implement, implement_id)

    def list_all(self, organization_id: UUID | None = None) -> list[Implement]:
        """Return all implements, optionally filtered by organization."""

        statement = select(Implement)
        if organization_id is not None:
            statement = statement.where(Implement.organization_id == organization_id)
        statement = statement.order_by(Implement.name.asc(), Implement.created_at.desc())
        return list(self._session.scalars(statement).all())

    def delete(self, implement: Implement) -> None:
        """Mark an implement for deletion in the current unit of work."""

        self._session.delete(implement)

