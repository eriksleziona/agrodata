"""User application service."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.organizations import OrganizationRepository
from app.repositories.users import UserRepository
from app.schemas.user import UserCreate
from app.services.errors import DuplicateUserEmailError, OrganizationNotFoundError


class UserService:
    """Coordinates organization-scoped user persistence.

    This service does not authenticate users or derive password hashes.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._organizations = OrganizationRepository(session)
        self._users = UserRepository(session)

    def create(self, data: UserCreate) -> User:
        """Create a user after enforcing organization and email invariants."""

        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(
                f"Organization {data.organization_id} was not found."
            )
        if self._users.get_by_organization_and_email(
            data.organization_id,
            data.email,
        ) is not None:
            raise DuplicateUserEmailError(
                "A user with this email already exists in the organization."
            )

        user = self._users.add(
            User(
                organization_id=data.organization_id,
                email=data.email,
                password_hash=data.password_hash,
                first_name=data.first_name,
                last_name=data.last_name,
                role=data.role,
            )
        )
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateUserEmailError(
                "A user with this email already exists in the organization."
            ) from error
        except Exception:
            self._session.rollback()
            raise
        self._session.refresh(user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by UUID, if it exists."""

        return self._users.get_by_id(user_id)
