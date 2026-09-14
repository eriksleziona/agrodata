"""Authentication application service: registration and login."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.organizations import OrganizationRepository
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserCreate
from app.services.errors import (
    DuplicateUserEmailError,
    InvalidCredentialsError,
    OrganizationNotFoundError,
)
from app.services.users import UserService


class AuthService:
    """Handles user registration, credential verification, and token issuance."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._organizations = OrganizationRepository(session)
        self._users = UserRepository(session)
        self._user_service = UserService(session)

    def register(self, data: RegisterRequest) -> User:
        """Register a new user: validate organization, hash password, persist.

        Raises:
            OrganizationNotFoundError: if organization_id does not exist.
            DuplicateUserEmailError: if email is already taken in this org.
        """

        if self._organizations.get_by_id(data.organization_id) is None:
            raise OrganizationNotFoundError(
                f"Organization {data.organization_id} was not found."
            )

        user_data = UserCreate(
            organization_id=data.organization_id,
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
        )
        return self._user_service.create(user_data)

    def login(self, data: LoginRequest) -> str:
        """Verify credentials and return a signed JWT access token.

        Raises:
            InvalidCredentialsError: if credentials do not match.
        """

        user = self._users.get_by_organization_and_email(
            data.organization_id,
            data.email,
        )
        if user is None or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError(
                "Invalid email, password, or organization."
            )

        return create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role.value,
        )
