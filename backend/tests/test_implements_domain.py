"""Tests for Implement domain model, repository, and service."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import CheckConstraint, inspect
from sqlalchemy.orm import Session

from app.models.implement import Implement
from app.models.organization import Organization
from app.schemas.implement import ImplementCreate, ImplementRead, ImplementUpdate
from app.schemas.organization import OrganizationCreate
from app.services.errors import (
    ImplementNotFoundError,
    InvalidWorkingWidthError,
    OrganizationNotFoundError,
)
from app.services.implements import ImplementService
from app.services.organizations import OrganizationService


def create_organization(session: Session, name: str = "AgroFarm", tax_id: str = "PL9876543210") -> Organization:
    """Helper to create an organization fixture."""

    return OrganizationService(session).create(
        OrganizationCreate(name=name, tax_id=tax_id)
    )


def test_implement_service_persists_all_fields(session: Session) -> None:
    """Implement is persisted with all specified fields, UUID, and UTC timestamps."""

    org = create_organization(session)
    service = ImplementService(session)

    created = service.create(
        ImplementCreate(
            organization_id=org.id,
            name="Lemken Juwel 8",
            manufacturer="Lemken",
            model="Juwel 8",
            type="PLOW",
            working_width=3.5,
        )
    )

    assert isinstance(created.id, UUID)
    assert created.organization_id == org.id
    assert created.name == "Lemken Juwel 8"
    assert created.manufacturer == "Lemken"
    assert created.model == "Juwel 8"
    assert created.type == "PLOW"
    assert created.working_width == 3.5
    assert inspect(Implement).columns.created_at.type.timezone is True
    assert inspect(Implement).columns.updated_at.type.timezone is True

    read_dto = ImplementRead.model_validate(created)
    assert read_dto.id == created.id
    assert read_dto.working_width == 3.5


def test_implement_service_supports_optional_and_trimmed_fields(session: Session) -> None:
    """Implement can be created with only required fields and strings are stripped."""

    org = create_organization(session)
    service = ImplementService(session)

    created = service.create(
        ImplementCreate(
            organization_id=org.id,
            name="  Horsch Pronto 6 DC  ",
            manufacturer="   ",
            model=None,
            type=None,
            working_width=6.0,
        )
    )

    assert created.name == "Horsch Pronto 6 DC"
    assert created.manufacturer is None
    assert created.model is None
    assert created.type is None
    assert created.working_width == 6.0


def test_implement_service_validates_working_width_positive(session: Session) -> None:
    """Working width must be strictly positive (> 0)."""

    org = create_organization(session)
    service = ImplementService(session)

    # Valid positive width
    created = service.create(
        ImplementCreate(
            organization_id=org.id,
            name="Cultivator",
            working_width=0.1,
        )
    )
    assert created.working_width == 0.1

    # Pydantic schema rejects <= 0
    with pytest.raises(Exception):
        ImplementCreate(
            organization_id=org.id,
            name="Invalid Zero Width",
            working_width=0.0,
        )

    with pytest.raises(Exception):
        ImplementCreate(
            organization_id=org.id,
            name="Invalid Negative Width",
            working_width=-2.5,
        )


def test_implement_service_rejects_nonexistent_organization(session: Session) -> None:
    """Creating an implement for a non-existent organization raises OrganizationNotFoundError."""

    service = ImplementService(session)
    with pytest.raises(OrganizationNotFoundError):
        service.create(
            ImplementCreate(
                organization_id=uuid4(),
                name="Orphan Implement",
                working_width=4.0,
            )
        )


def test_implement_get_by_id_and_not_found(session: Session) -> None:
    """Retrieving an implement by UUID works or raises ImplementNotFoundError."""

    org = create_organization(session)
    service = ImplementService(session)
    implement = service.create(
        ImplementCreate(organization_id=org.id, name="Seeder 1", working_width=4.0)
    )

    fetched = service.get_by_id(implement.id)
    assert fetched.id == implement.id

    with pytest.raises(ImplementNotFoundError):
        service.get_by_id(uuid4())


def test_implement_list_all_and_filter_by_organization(session: Session) -> None:
    """Implements can be listed globally or filtered by organization."""

    org1 = create_organization(session, tax_id="PL-IMP-1")
    org2 = create_organization(session, tax_id="PL-IMP-2")
    service = ImplementService(session)

    service.create(ImplementCreate(organization_id=org1.id, name="Org1-I1", working_width=3.0))
    service.create(ImplementCreate(organization_id=org1.id, name="Org1-I2", working_width=6.0))
    service.create(ImplementCreate(organization_id=org2.id, name="Org2-I1", working_width=9.0))

    all_implements = service.list_all()
    assert len(all_implements) == 3

    org1_implements = service.list_all(organization_id=org1.id)
    assert len(org1_implements) == 2
    assert {i.name for i in org1_implements} == {"Org1-I1", "Org1-I2"}

    with pytest.raises(OrganizationNotFoundError):
        service.list_all(organization_id=uuid4())


def test_implement_update_and_validation(session: Session) -> None:
    """Implement fields can be updated, and non-positive working_width is rejected."""

    org = create_organization(session)
    service = ImplementService(session)

    implement = service.create(
        ImplementCreate(
            organization_id=org.id,
            name="Original Implement",
            working_width=3.0,
        )
    )

    updated = service.update(
        implement.id,
        ImplementUpdate(name="Updated Implement", working_width=4.5),
    )
    assert updated.name == "Updated Implement"
    assert updated.working_width == 4.5

    with pytest.raises(ImplementNotFoundError):
        service.update(uuid4(), ImplementUpdate(name="Ghost"))


def test_implement_delete(session: Session) -> None:
    """Implement can be deleted by UUID."""

    org = create_organization(session)
    service = ImplementService(session)
    implement = service.create(
        ImplementCreate(organization_id=org.id, name="To Delete", working_width=2.0)
    )

    service.delete(implement.id)

    with pytest.raises(ImplementNotFoundError):
        service.get_by_id(implement.id)

    with pytest.raises(ImplementNotFoundError):
        service.delete(uuid4())


def test_implement_model_constraints_and_indexes() -> None:
    """Implement model defines the required indexes and check constraint."""

    indexes = {idx.name for idx in Implement.__table__.indexes}
    check_constraints = [
        c for c in Implement.__table__.constraints if isinstance(c, CheckConstraint)
    ]

    assert "ix_implements_organization_id" in indexes
    assert any("working_width > 0" in str(c.sqltext) for c in check_constraints)

