"""Authentication API endpoints: register, login, me."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, DBSessionDep
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, session: DBSessionDep) -> UserRead:
    """Register a new organization-scoped user.

    Returns the created user profile. Password is never included in the response.
    """

    user = AuthService(session).register(data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: DBSessionDep) -> TokenResponse:
    """Authenticate with email, password, and organization, and return a JWT."""

    token = AuthService(session).login(data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUserDep) -> UserRead:
    """Return the profile of the currently authenticated user."""

    return UserRead.model_validate(current_user)
