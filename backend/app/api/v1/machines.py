"""Machines API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import (
    CurrentUserDep,
    DBSessionDep,
    DELETER_ROLES,
    WRITER_ROLES,
)
from app.models.user import User
from app.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from app.services.machines import MachineService

router = APIRouter(prefix="/machines", tags=["machines"])


def _check_org(resource_org: UUID, current_user: User) -> None:
    """Raise HTTP 404 if *resource_org* does not belong to the current user's org.

    Returns 404 (not 403) to avoid leaking existence of cross-org resources.
    """

    if resource_org != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found.")


def _require_writer(current_user: User) -> None:
    if current_user.role not in WRITER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of: {', '.join(r.value for r in WRITER_ROLES)}.",
        )


def _require_deleter(current_user: User) -> None:
    if current_user.role not in DELETER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires one of: {', '.join(r.value for r in DELETER_ROLES)}.",
        )


@router.get("", response_model=list[MachineRead])
def list_machines(
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> list[MachineRead]:
    """Retrieve all machines belonging to the authenticated user's organization."""

    machines = MachineService(session).list_all(organization_id=current_user.organization_id)
    return [MachineRead.model_validate(m) for m in machines]


@router.post("", response_model=MachineRead, status_code=status.HTTP_201_CREATED)
def create_machine(
    data: MachineCreate,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> MachineRead:
    """Create a new machine within the authenticated user's organization."""

    _require_writer(current_user)
    scoped = data.model_copy(update={"organization_id": current_user.organization_id})
    machine = MachineService(session).create(scoped)
    return MachineRead.model_validate(machine)


@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(
    machine_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> MachineRead:
    """Retrieve a machine by ID, scoped to the authenticated organization."""

    machine = MachineService(session).get_by_id(machine_id)
    _check_org(machine.organization_id, current_user)
    return MachineRead.model_validate(machine)


@router.put("/{machine_id}", response_model=MachineRead)
def update_machine(
    machine_id: UUID,
    data: MachineUpdate,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> MachineRead:
    """Update an existing machine, scoped to the authenticated organization."""

    _require_writer(current_user)
    service = MachineService(session)
    machine = service.get_by_id(machine_id)
    _check_org(machine.organization_id, current_user)
    machine = service.update(machine_id, data)
    return MachineRead.model_validate(machine)


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(
    machine_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> Response:
    """Delete a machine by ID, scoped to the authenticated organization."""

    _require_deleter(current_user)
    service = MachineService(session)
    machine = service.get_by_id(machine_id)
    _check_org(machine.organization_id, current_user)
    service.delete(machine_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
