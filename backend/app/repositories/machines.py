"""Machine persistence operations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.machine import Machine


class MachineRepository:
    """Database access operations for machines."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, machine: Machine) -> Machine:
        """Add a machine to the current unit of work."""

        self._session.add(machine)
        return machine

    def get_by_id(self, machine_id: UUID) -> Machine | None:
        """Return a machine by its UUID, if it exists."""

        return self._session.get(Machine, machine_id)

    def get_by_device_id(self, device_id: str) -> Machine | None:
        """Return a machine by its associated device_id, if present."""

        statement = select(Machine).where(Machine.device_id == device_id)
        return self._session.scalar(statement)

    def list_all(self, organization_id: UUID | None = None) -> list[Machine]:
        """Return all machines, optionally filtered by organization."""

        statement = select(Machine)
        if organization_id is not None:
            statement = statement.where(Machine.organization_id == organization_id)
        statement = statement.order_by(Machine.name.asc(), Machine.created_at.desc())
        return list(self._session.scalars(statement).all())

    def delete(self, machine: Machine) -> None:
        """Mark a machine for deletion in the current unit of work."""

        self._session.delete(machine)

