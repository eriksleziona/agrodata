"""Tests for Machine domain model, repository, and service."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import UniqueConstraint, inspect
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.organization import Organization
from app.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from app.schemas.organization import OrganizationCreate
from app.services.errors import (
    DuplicateDeviceIdError,
    MachineNotFoundError,
    OrganizationNotFoundError,
)
from app.services.machines import MachineService
from app.services.organizations import OrganizationService


def create_organization(session: Session, name: str = "AgroFarm", tax_id: str = "PL9876543210") -> Organization:
    """Helper to create an organization fixture."""

    return OrganizationService(session).create(
        OrganizationCreate(name=name, tax_id=tax_id)
    )


def test_machine_service_persists_all_fields(session: Session) -> None:
    """Machine is persisted with all specified fields, UUID, and UTC timestamps."""

    org = create_organization(session)
    service = MachineService(session)

    created = service.create(
        MachineCreate(
            organization_id=org.id,
            name="John Deere 8R 410",
            manufacturer="John Deere",
            model="8R 410",
            serial_number="1RW8410RLPR012345",
            year=2024,
            power_hp=410,
            device_id="AGRO-EDGE-001",
        )
    )

    assert isinstance(created.id, UUID)
    assert created.organization_id == org.id
    assert created.name == "John Deere 8R 410"
    assert created.manufacturer == "John Deere"
    assert created.model == "8R 410"
    assert created.serial_number == "1RW8410RLPR012345"
    assert created.year == 2024
    assert created.power_hp == 410
    assert created.device_id == "AGRO-EDGE-001"
    assert inspect(Machine).columns.created_at.type.timezone is True
    assert inspect(Machine).columns.updated_at.type.timezone is True

    # Pydantic schema validation
    read_dto = MachineRead.model_validate(created)
    assert read_dto.id == created.id
    assert read_dto.name == "John Deere 8R 410"
    assert read_dto.device_id == "AGRO-EDGE-001"


def test_machine_service_supports_optional_and_trimmed_fields(session: Session) -> None:
    """Machine can be created with only required fields and strings are stripped."""

    org = create_organization(session)
    service = MachineService(session)

    created = service.create(
        MachineCreate(
            organization_id=org.id,
            name="  Fendt 724 Vario  ",
            manufacturer="   ",
            model=None,
            serial_number=None,
            year=None,
            power_hp=None,
            device_id=None,
        )
    )

    assert created.name == "Fendt 724 Vario"
    assert created.manufacturer is None
    assert created.model is None
    assert created.serial_number is None
    assert created.year is None
    assert created.power_hp is None
    assert created.device_id is None


def test_machine_device_id_must_be_unique(session: Session) -> None:
    """Duplicate device_id is rejected across all machines."""

    org1 = create_organization(session, tax_id="PL1111111111")
    org2 = create_organization(session, tax_id="PL2222222222")
    service = MachineService(session)

    service.create(
        MachineCreate(
            organization_id=org1.id,
            name="Tractor A",
            device_id="DEV-UNIQUE-100",
        )
    )

    with pytest.raises(DuplicateDeviceIdError):
        service.create(
            MachineCreate(
                organization_id=org2.id,
                name="Tractor B",
                device_id="DEV-UNIQUE-100",
            )
        )


def test_multiple_machines_with_null_device_id_allowed(session: Session) -> None:
    """Multiple machines can exist without an assigned device_id."""

    org = create_organization(session)
    service = MachineService(session)

    m1 = service.create(MachineCreate(organization_id=org.id, name="Combine 1"))
    m2 = service.create(MachineCreate(organization_id=org.id, name="Combine 2"))

    assert m1.device_id is None
    assert m2.device_id is None
    assert m1.id != m2.id


def test_machine_service_rejects_nonexistent_organization(session: Session) -> None:
    """Creating a machine for a non-existent organization raises OrganizationNotFoundError."""

    service = MachineService(session)
    with pytest.raises(OrganizationNotFoundError):
        service.create(
            MachineCreate(
                organization_id=uuid4(),
                name="Orphan Machine",
            )
        )


def test_machine_get_by_id_and_not_found(session: Session) -> None:
    """Retrieving a machine by UUID works or raises MachineNotFoundError."""

    org = create_organization(session)
    service = MachineService(session)
    machine = service.create(MachineCreate(organization_id=org.id, name="Sprayer 1"))

    fetched = service.get_by_id(machine.id)
    assert fetched.id == machine.id

    with pytest.raises(MachineNotFoundError):
        service.get_by_id(uuid4())


def test_machine_list_all_and_filter_by_organization(session: Session) -> None:
    """Machines can be listed globally or filtered by organization."""

    org1 = create_organization(session, tax_id="PL-ORG-1")
    org2 = create_organization(session, tax_id="PL-ORG-2")
    service = MachineService(session)

    service.create(MachineCreate(organization_id=org1.id, name="Org1-M1"))
    service.create(MachineCreate(organization_id=org1.id, name="Org1-M2"))
    service.create(MachineCreate(organization_id=org2.id, name="Org2-M1"))

    all_machines = service.list_all()
    assert len(all_machines) == 3

    org1_machines = service.list_all(organization_id=org1.id)
    assert len(org1_machines) == 2
    assert {m.name for m in org1_machines} == {"Org1-M1", "Org1-M2"}

    with pytest.raises(OrganizationNotFoundError):
        service.list_all(organization_id=uuid4())


def test_machine_update_and_conflict_handling(session: Session) -> None:
    """Machine fields can be updated, and conflicting device_id is rejected."""

    org = create_organization(session)
    service = MachineService(session)

    m1 = service.create(
        MachineCreate(
            organization_id=org.id,
            name="Original Name",
            power_hp=200,
            device_id="DEV-A",
        )
    )
    m2 = service.create(
        MachineCreate(
            organization_id=org.id,
            name="Second Machine",
            device_id="DEV-B",
        )
    )

    updated = service.update(
        m1.id,
        MachineUpdate(name="Updated Name", power_hp=250),
    )
    assert updated.name == "Updated Name"
    assert updated.power_hp == 250
    assert updated.device_id == "DEV-A"

    # Updating to same device_id is allowed
    service.update(m1.id, MachineUpdate(device_id="DEV-A"))

    # Updating to existing other machine's device_id is rejected
    with pytest.raises(DuplicateDeviceIdError):
        service.update(m1.id, MachineUpdate(device_id="DEV-B"))

    # Updating non-existent machine raises MachineNotFoundError
    with pytest.raises(MachineNotFoundError):
        service.update(uuid4(), MachineUpdate(name="Ghost"))


def test_machine_delete(session: Session) -> None:
    """Machine can be deleted by UUID."""

    org = create_organization(session)
    service = MachineService(session)
    machine = service.create(MachineCreate(organization_id=org.id, name="To Delete"))

    service.delete(machine.id)

    with pytest.raises(MachineNotFoundError):
        service.get_by_id(machine.id)

    with pytest.raises(MachineNotFoundError):
        service.delete(uuid4())


def test_machine_model_constraints_and_indexes() -> None:
    """Machine model defines the required indexes and unique constraint."""

    indexes = {idx.name for idx in Machine.__table__.indexes}
    unique_constraints = {
        uc.name for uc in Machine.__table__.constraints if isinstance(uc, UniqueConstraint)
    }

    assert "ix_machines_organization_id" in indexes
    assert "ix_machines_device_id" in indexes
    assert "uq_machines_device_id" in unique_constraints

