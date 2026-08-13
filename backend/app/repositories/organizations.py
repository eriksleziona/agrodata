"""Organization persistence operations."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    """Database access operations for organizations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, organization: Organization) -> Organization:
        """Add an organization to the current unit of work."""

        self._session.add(organization)
        return organization

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        """Return an organization by its UUID, if it exists."""

        return self._session.get(Organization, organization_id)
