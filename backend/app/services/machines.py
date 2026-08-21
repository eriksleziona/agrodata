"""Machine application service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.repositories.machines import MachineRepository
from app.repositories.organizations import OrganizationRepository
from app.schemas.machine import MachineCreate, MachineUpdate
from app.services.errors import (
    DuplicateDeviceIdError,
    MachineNotFoundError,
    OrganizationNotFoundError,
)


class MachineService:
    """Coordinates machine persistence and enforces domain invariants."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._organizations = OrganizationRepository(session)
        self._machines = MachineRepository(session)

    def create(self, data: MachineCreate) -> Machine:
        """Create and persist a new machine after validating invariants."""

        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(
                f"Organization {data.organization_id} was not found."
            )

        if data.device_id is not None:
            existing = self._machines.get_by_device_id(data.device_id)
            if existing is not None:
                raise DuplicateDeviceIdError(
                    f"A machine with device_id '{data.device_id}' already exists."
                )

        machine = self._machines.add(
            Machine(
                organization_id=data.organization_id,
                name=data.name,
                manufacturer=data.manufacturer,
                model=data.model,
                serial_number=data.serial_number,
                year=data.year,
                power_hp=data.power_hp,
                device_id=data.device_id,
            )
        )
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateDeviceIdError(
                f"A machine with device_id '{data.device_id}' already exists."
            ) from error
        except Exception:
            self._session.rollback()
            raise

        self._session.refresh(machine)
        return machine

    def get_by_id(self, machine_id: UUID) -> Machine:
        """Return a machine by its UUID or raise MachineNotFoundError."""

        machine = self._machines.get_by_id(machine_id)
        if machine is None:
            raise MachineNotFoundError(f"Machine {machine_id} was not found.")
        return machine

    def list_all(self, organization_id: UUID | None = None) -> list[Machine]:
        """Return all machines, optionally filtered by organization."""

        if (
            organization_id is not None
            and self._organizations.get_by_id(organization_id) is None
        ):
            raise OrganizationNotFoundError(
                f"Organization {organization_id} was not found."
            )

        return self._machines.list_all(organization_id=organization_id)

    def update(self, machine_id: UUID, data: MachineUpdate) -> Machine:
        """Update an existing machine's attributes."""

        machine = self.get_by_id(machine_id)
        update_data = data.model_dump(exclude_unset=True)

        if "device_id" in update_data:
            new_device_id = update_data["device_id"]
            if new_device_id is not None and new_device_id != machine.device_id:
                existing = self._machines.get_by_device_id(new_device_id)
                if existing is not None and existing.id != machine.id:
                    raise DuplicateDeviceIdError(
                        f"A machine with device_id '{new_device_id}' already exists."
                    )

        for field, value in update_data.items():
            setattr(machine, field, value)

        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateDeviceIdError(
                f"A machine with device_id '{update_data.get('device_id')}' already exists."
            ) from error
        except Exception:
            self._session.rollback()
            raise

        self._session.refresh(machine)
        return machine

    def delete(self, machine_id: UUID) -> None:
        """Delete a machine by its UUID."""

        machine = self.get_by_id(machine_id)
        self._machines.delete(machine)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

