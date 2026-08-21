"""Agricultural implements API endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.deps import DBSessionDep
from app.schemas.implement import ImplementCreate, ImplementRead, ImplementUpdate
from app.services.implements import ImplementService

router = APIRouter(prefix="/implements", tags=["implements"])


@router.get("", response_model=list[ImplementRead])
def list_implements(
    session: DBSessionDep,
    organization_id: UUID | None = None,
) -> list[ImplementRead]:
    """Retrieve all implements, optionally filtered by organization."""

    service = ImplementService(session)
    implements = service.list_all(organization_id=organization_id)
    return [ImplementRead.model_validate(item) for item in implements]


@router.post("", response_model=ImplementRead, status_code=status.HTTP_201_CREATED)
def create_implement(
    data: ImplementCreate,
    session: DBSessionDep,
) -> ImplementRead:
    """Create a new agricultural implement within an organization."""

    service = ImplementService(session)
    implement = service.create(data)
    return ImplementRead.model_validate(implement)


@router.get("/{implement_id}", response_model=ImplementRead)
def get_implement(
    implement_id: UUID,
    session: DBSessionDep,
) -> ImplementRead:
    """Retrieve an agricultural implement by its unique identifier."""

    service = ImplementService(session)
    implement = service.get_by_id(implement_id)
    return ImplementRead.model_validate(implement)


@router.put("/{implement_id}", response_model=ImplementRead)
def update_implement(
    implement_id: UUID,
    data: ImplementUpdate,
    session: DBSessionDep,
) -> ImplementRead:
    """Update an existing agricultural implement's attributes."""

    service = ImplementService(session)
    implement = service.update(implement_id, data)
    return ImplementRead.model_validate(implement)


@router.delete("/{implement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_implement(
    implement_id: UUID,
    session: DBSessionDep,
) -> Response:
    """Delete an agricultural implement by its unique identifier."""

    service = ImplementService(session)
    service.delete(implement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

