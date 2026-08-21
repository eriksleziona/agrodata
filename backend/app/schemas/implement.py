"""Implement input and output schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ImplementCreate(BaseModel):
    """Data required to create an organization-scoped agricultural implement."""

    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    type: str | None = Field(default=None, max_length=100)
    working_width: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def strip_required_name(cls, value: str) -> str:
        """Reject blank name after trimming surrounding whitespace."""

        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized

    @field_validator("manufacturer", "model", "type")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace and normalize blank strings to None."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None


class ImplementUpdate(BaseModel):
    """Data accepted when updating an existing agricultural implement."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    type: str | None = Field(default=None, max_length=100)
    working_width: float | None = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        """Reject blank name after trimming surrounding whitespace if provided."""

        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized

    @field_validator("manufacturer", "model", "type")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace and normalize blank strings to None."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None


class ImplementRead(BaseModel):
    """Implement representation safe for external API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    manufacturer: str | None
    model: str | None
    type: str | None
    working_width: float
    created_at: datetime
    updated_at: datetime

