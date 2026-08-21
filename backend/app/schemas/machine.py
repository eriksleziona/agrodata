"""Machine input and output schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MachineCreate(BaseModel):
    """Data required to create an organization-scoped machine."""

    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    power_hp: int | None = Field(default=None, ge=0)
    device_id: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_required_name(cls, value: str) -> str:
        """Reject blank name after trimming surrounding whitespace."""

        normalized = value.strip()
        if not normalized:
            message = "Value must not be blank."
            raise ValueError(message)
        return normalized

    @field_validator("manufacturer", "model", "serial_number", "device_id")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace and normalize blank strings to None."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None


class MachineUpdate(BaseModel):
    """Data accepted when updating an existing machine."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=1900, le=2100)
    power_hp: int | None = Field(default=None, ge=0)
    device_id: str | None = Field(default=None, max_length=100)

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

    @field_validator("manufacturer", "model", "serial_number", "device_id")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        """Strip surrounding whitespace and normalize blank strings to None."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None


class MachineRead(BaseModel):
    """Machine representation safe for external API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    manufacturer: str | None
    model: str | None
    serial_number: str | None
    year: int | None
    power_hp: int | None
    device_id: str | None
    created_at: datetime
    updated_at: datetime

