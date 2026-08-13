"""User persistence operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Database access operations for organization-scoped users."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        """Add a user to the current unit of work."""

        self._session.add(user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by UUID, if it exists."""

        return self._session.get(User, user_id)

    def get_by_organization_and_email(
        self,
        organization_id: UUID,
        email: str,
    ) -> User | None:
        """Return a user with an email inside one organization, if present."""

        statement = select(User).where(
            User.organization_id == organization_id,
            User.email == email,
        )
        return self._session.scalar(statement)
