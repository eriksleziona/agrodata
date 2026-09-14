"""Authentication input and output schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    """Data required to register a new user account."""

    organization_id: UUID
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.OPERATOR

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase and strip email."""

        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@"):
            raise ValueError("Email must contain a local part and domain.")
        return normalized

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Reject blank values after stripping whitespace."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("Value must not be blank.")
        return normalized


class LoginRequest(BaseModel):
    """Credentials required to obtain an access token."""

    organization_id: UUID
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase and strip email."""

        return value.strip().lower()


class TokenResponse(BaseModel):
    """JWT access token returned on successful login."""

    access_token: str
    token_type: str = "bearer"
