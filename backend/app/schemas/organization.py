"""Organization input and output schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrganizationCreate(BaseModel):
    """Data required to create an organization."""

    name: str = Field(min_length=1, max_length=255)
    tax_id: str = Field(min_length=1, max_length=64)

    @field_validator("name", "tax_id")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        """Reject blank values after trimming surrounding whitespace."""

        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized


class OrganizationRead(BaseModel):
    """Organization data safe to expose outside the persistence layer."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    tax_id: str
    created_at: datetime
    updated_at: datetime
