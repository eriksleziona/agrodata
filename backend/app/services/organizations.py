"""Organization application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.organizations import OrganizationRepository
from app.schemas.organization import OrganizationCreate
from app.services.errors import OrganizationNotFoundError


class OrganizationService:
    """Coordinates organization persistence without exposing ORM details."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = OrganizationRepository(session)

    def create(self, data: OrganizationCreate) -> Organization:
        """Create and persist an organization."""

        organization = self._repository.add(
            Organization(name=data.name, tax_id=data.tax_id)
        )
        self._commit_and_refresh(organization)
        return organization

    def get_by_id(self, organization_id: UUID) -> Organization:
        """Return an organization or raise a service-level not-found error."""

        organization = self._repository.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(
                f"Organization {organization_id} was not found."
            )
        return organization

    def _commit_and_refresh(self, organization: Organization) -> None:
        """Commit the current unit of work and return refreshed state."""

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        self._session.refresh(organization)
