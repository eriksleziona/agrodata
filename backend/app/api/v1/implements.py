"""Agricultural implements API endpoints."""

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
from app.schemas.implement import ImplementCreate, ImplementRead, ImplementUpdate
from app.services.implements import ImplementService

router = APIRouter(prefix="/implements", tags=["implements"])


def _check_org(resource_org: UUID, current_user: User) -> None:
    """Raise HTTP 404 if *resource_org* differs from the current user's org."""

    if resource_org != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Implement not found.")


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


@router.get("", response_model=list[ImplementRead])
def list_implements(
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> list[ImplementRead]:
    """Retrieve all implements belonging to the authenticated user's organization."""

    implements = ImplementService(session).list_all(organization_id=current_user.organization_id)
    return [ImplementRead.model_validate(item) for item in implements]


@router.post("", response_model=ImplementRead, status_code=status.HTTP_201_CREATED)
def create_implement(
    data: ImplementCreate,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> ImplementRead:
    """Create a new agricultural implement within the authenticated organization."""

    _require_writer(current_user)
    scoped = data.model_copy(update={"organization_id": current_user.organization_id})
    implement = ImplementService(session).create(scoped)
    return ImplementRead.model_validate(implement)


@router.get("/{implement_id}", response_model=ImplementRead)
def get_implement(
    implement_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> ImplementRead:
    """Retrieve an implement by ID, scoped to the authenticated organization."""

    implement = ImplementService(session).get_by_id(implement_id)
    _check_org(implement.organization_id, current_user)
    return ImplementRead.model_validate(implement)


@router.put("/{implement_id}", response_model=ImplementRead)
def update_implement(
    implement_id: UUID,
    data: ImplementUpdate,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> ImplementRead:
    """Update an existing implement, scoped to the authenticated organization."""

    _require_writer(current_user)
    service = ImplementService(session)
    implement = service.get_by_id(implement_id)
    _check_org(implement.organization_id, current_user)
    implement = service.update(implement_id, data)
    return ImplementRead.model_validate(implement)


@router.delete("/{implement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_implement(
    implement_id: UUID,
    current_user: CurrentUserDep,
    session: DBSessionDep,
) -> Response:
    """Delete an implement by ID, scoped to the authenticated organization."""

    _require_deleter(current_user)
    service = ImplementService(session)
    implement = service.get_by_id(implement_id)
    _check_org(implement.organization_id, current_user)
    service.delete(implement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
