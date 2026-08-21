"""Implement application service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.implement import Implement
from app.repositories.implements import ImplementRepository
from app.repositories.organizations import OrganizationRepository
from app.schemas.implement import ImplementCreate, ImplementUpdate
from app.services.errors import (
    ImplementNotFoundError,
    InvalidWorkingWidthError,
    OrganizationNotFoundError,
)


class ImplementService:
    """Coordinates agricultural implement persistence and enforces domain invariants."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._organizations = OrganizationRepository(session)
        self._implements = ImplementRepository(session)

    def create(self, data: ImplementCreate) -> Implement:
        """Create and persist a new implement after validating invariants."""

        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(
                f"Organization {data.organization_id} was not found."
            )

        if data.working_width <= 0:
            raise InvalidWorkingWidthError("Working width must be greater than 0.")

        implement = self._implements.add(
            Implement(
                organization_id=data.organization_id,
                name=data.name,
                manufacturer=data.manufacturer,
                model=data.model,
                type=data.type,
                working_width=data.working_width,
            )
        )
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

        self._session.refresh(implement)
        return implement

    def get_by_id(self, implement_id: UUID) -> Implement:
        """Return an implement by its UUID or raise ImplementNotFoundError."""

        implement = self._implements.get_by_id(implement_id)
        if implement is None:
            raise ImplementNotFoundError(f"Implement {implement_id} was not found.")
        return implement

    def list_all(self, organization_id: UUID | None = None) -> list[Implement]:
        """Return all implements, optionally filtered by organization."""

        if (
            organization_id is not None
            and self._organizations.get_by_id(organization_id) is None
        ):
            raise OrganizationNotFoundError(
                f"Organization {organization_id} was not found."
            )

        return self._implements.list_all(organization_id=organization_id)

    def update(self, implement_id: UUID, data: ImplementUpdate) -> Implement:
        """Update an existing implement's attributes."""

        implement = self.get_by_id(implement_id)
        update_data = data.model_dump(exclude_unset=True)

        if "working_width" in update_data:
            width = update_data["working_width"]
            if width is not None and width <= 0:
                raise InvalidWorkingWidthError("Working width must be greater than 0.")

        for field, value in update_data.items():
            setattr(implement, field, value)

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

        self._session.refresh(implement)
        return implement

    def delete(self, implement_id: UUID) -> None:
        """Delete an implement by its UUID."""

        implement = self.get_by_id(implement_id)
        self._implements.delete(implement)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

