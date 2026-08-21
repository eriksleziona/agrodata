"""Machines API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.deps import DBSessionDep
from app.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from app.services.machines import MachineService

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get("", response_model=list[MachineRead])
def list_machines(
    session: DBSessionDep,
    organization_id: UUID | None = None,
) -> list[MachineRead]:
    """Retrieve all machines, optionally filtered by organization."""

    service = MachineService(session)
    machines = service.list_all(organization_id=organization_id)
    return [MachineRead.model_validate(m) for m in machines]


@router.post("", response_model=MachineRead, status_code=status.HTTP_201_CREATED)
def create_machine(
    data: MachineCreate,
    session: DBSessionDep,
) -> MachineRead:
    """Create a new machine within an organization."""

    service = MachineService(session)
    machine = service.create(data)
    return MachineRead.model_validate(machine)


@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(
    machine_id: UUID,
    session: DBSessionDep,
) -> MachineRead:
    """Retrieve a machine by its unique identifier."""

    service = MachineService(session)
    machine = service.get_by_id(machine_id)
    return MachineRead.model_validate(machine)


@router.put("/{machine_id}", response_model=MachineRead)
def update_machine(
    machine_id: UUID,
    data: MachineUpdate,
    session: DBSessionDep,
) -> MachineRead:
    """Update an existing machine's attributes."""

    service = MachineService(session)
    machine = service.update(machine_id, data)
    return MachineRead.model_validate(machine)


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(
    machine_id: UUID,
    session: DBSessionDep,
) -> Response:
    """Delete a machine by its unique identifier."""

    service = MachineService(session)
    service.delete(machine_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

