"""User input and output schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Data required to create an organization-scoped user.

    ``password_hash`` is an already-derived opaque value. Password hashing and
    authentication flows are intentionally not part of this foundation.
    """

    organization_id: UUID
    email: str = Field(min_length=3, max_length=320)
    password_hash: str = Field(min_length=1, max_length=1024)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: UserRole

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email values used by the organization-level constraint."""

        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@"):
            message = "Email must contain a local part and domain."
            raise ValueError(message)
        return normalized

    @field_validator("password_hash", "first_name", "last_name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Reject blank text after trimming surrounding whitespace."""

        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized


class UserRead(BaseModel):
    """User data safe to expose outside the persistence layer."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
