"""Tests for Job domain model, repository, service, and state transitions."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.implement import Implement
from app.models.job import Job, JobStatus
from app.models.machine import Machine
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.implement import ImplementCreate
from app.schemas.job import JobCreate, JobFinish, JobRead
from app.schemas.machine import MachineCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
from app.services.errors import (
    ImplementNotFoundError,
    InvalidJobStateTransitionError,
    JobNotFoundError,
    MachineNotFoundError,
    OrganizationNotFoundError,
)
from app.services.implements import ImplementService
from app.services.jobs import JobService
from app.services.machines import MachineService
from app.services.organizations import OrganizationService
from app.services.users import UserService


def create_organization(session: Session, name: str = "Job Farm", tax_id: str = "PL9999999999") -> Organization:
    """Helper to create an organization fixture."""

    return OrganizationService(session).create(
        OrganizationCreate(name=name, tax_id=tax_id)
    )


def create_machine(session: Session, org_id: UUID, name: str = "Tractor 1") -> Machine:
    """Helper to create a machine fixture."""

    return MachineService(session).create(
        MachineCreate(organization_id=org_id, name=name)
    )


def create_implement(session: Session, org_id: UUID, name: str = "Plow 1") -> Implement:
    """Helper to create an implement fixture."""

    return ImplementService(session).create(
        ImplementCreate(organization_id=org_id, name=name, working_width=3.0)
    )


def create_operator(session: Session, org_id: UUID, email: str = "op@example.com") -> User:
    """Helper to create an operator user fixture."""

    return UserService(session).create(
        UserCreate(
            organization_id=org_id,
            email=email,
            password_hash="hash",
            first_name="Jan",
            last_name="Kowalski",
            role=UserRole.OPERATOR,
        )
    )


def test_job_service_persists_all_fields_and_defaults(session: Session) -> None:
    """Job is persisted with all relationships, initial PLANNED status, and default metrics."""

    org = create_organization(session)
    machine = create_machine(session, org.id)
    implement = create_implement(session, org.id)
    operator = create_operator(session, org.id)
    service = JobService(session)

    farm_id = uuid4()
    field_id = uuid4()

    job = service.create(
        JobCreate(
            organization_id=org.id,
            farm_id=farm_id,
            field_id=field_id,
            machine_id=machine.id,
            implement_id=implement.id,
            operator_id=operator.id,
            type="HARVESTING",
            area_planned=15.5,
        )
    )

    assert isinstance(job.id, UUID)
    assert job.organization_id == org.id
    assert job.farm_id == farm_id
    assert job.field_id == field_id
    assert job.machine_id == machine.id
    assert job.implement_id == implement.id
    assert job.operator_id == operator.id
    assert job.type == "HARVESTING"
    assert job.status is JobStatus.PLANNED
    assert job.started_at is None
    assert job.finished_at is None
    assert job.area_planned == 15.5
    assert job.area_completed == 0.0
    assert job.distance == 0.0
    assert job.working_time == 0
    assert job.idle_time == 0
    assert job.fuel_used == 0.0
    assert inspect(Job).columns.created_at.type.timezone is True
    assert inspect(Job).columns.updated_at.type.timezone is True

    read_dto = JobRead.model_validate(job)
    assert read_dto.id == job.id
    assert read_dto.status is JobStatus.PLANNED


def test_job_service_validates_foreign_references(session: Session) -> None:
    """Foreign IDs must belong to the organization."""

    org1 = create_organization(session, tax_id="PL-ORG-1")
    org2 = create_organization(session, tax_id="PL-ORG-2")
    m2 = create_machine(session, org2.id)
    i2 = create_implement(session, org2.id)
    u2 = create_operator(session, org2.id, email="u2@example.com")
    service = JobService(session)

    # Missing organization
    with pytest.raises(OrganizationNotFoundError):
        service.create(JobCreate(organization_id=uuid4(), type="SPRAYING"))

    # Machine from different org
    with pytest.raises(MachineNotFoundError):
        service.create(
            JobCreate(organization_id=org1.id, machine_id=m2.id, type="SPRAYING")
        )

    # Implement from different org
    with pytest.raises(ImplementNotFoundError):
        service.create(
            JobCreate(organization_id=org1.id, implement_id=i2.id, type="SPRAYING")
        )

    # Operator from different org
    with pytest.raises(OrganizationNotFoundError):
        service.create(
            JobCreate(organization_id=org1.id, operator_id=u2.id, type="SPRAYING")
        )


def test_job_state_transitions_full_lifecycle(session: Session) -> None:
    """Test standard lifecycle PLANNED -> STARTED -> PAUSED -> STARTED -> COMPLETED."""

    org = create_organization(session)
    service = JobService(session)

    job = service.create(JobCreate(organization_id=org.id, type="SEEDING"))
    assert job.status is JobStatus.PLANNED
    assert job.started_at is None

    # PLANNED -> STARTED
    job = service.start(job.id)
    assert job.status is JobStatus.STARTED
    assert job.started_at is not None
    start_time = job.started_at

    # STARTED -> PAUSED
    job = service.pause(job.id)
    assert job.status is JobStatus.PAUSED

    # PAUSED -> STARTED (resume)
    job = service.resume(job.id)
    assert job.status is JobStatus.STARTED
    assert job.started_at == start_time  # Preserves initial start timestamp

    # STARTED -> COMPLETED (finish with metrics)
    metrics = JobFinish(
        area_completed=12.4,
        distance=8500.0,
        working_time=3600,
        idle_time=400,
        fuel_used=24.5,
    )
    job = service.finish(job.id, metrics=metrics)
    assert job.status is JobStatus.COMPLETED
    assert job.finished_at is not None
    assert job.area_completed == 12.4
    assert job.distance == 8500.0
    assert job.working_time == 3600
    assert job.idle_time == 400
    assert job.fuel_used == 24.5


def test_job_state_transitions_finish_from_paused(session: Session) -> None:
    """Job can be finished directly from PAUSED."""

    org = create_organization(session)
    service = JobService(session)

    job = service.create(JobCreate(organization_id=org.id, type="SEEDING"))
    service.start(job.id)
    service.pause(job.id)

    job = service.finish(job.id)
    assert job.status is JobStatus.COMPLETED
    assert job.finished_at is not None


@pytest.mark.parametrize("initial_status", [JobStatus.PLANNED, JobStatus.STARTED, JobStatus.PAUSED])
def test_job_cancel_from_non_terminal_states(
    session: Session,
    initial_status: JobStatus,
) -> None:
    """Job can be cancelled from PLANNED, STARTED, and PAUSED."""

    org = create_organization(session, tax_id=f"PL-{initial_status.value}")
    service = JobService(session)

    job = service.create(JobCreate(organization_id=org.id, type="TILLAGE"))
    if initial_status == JobStatus.STARTED:
        service.start(job.id)
    elif initial_status == JobStatus.PAUSED:
        service.start(job.id)
        service.pause(job.id)

    cancelled = service.cancel(job.id)
    assert cancelled.status is JobStatus.CANCELLED
    assert cancelled.finished_at is not None


def test_job_rejects_invalid_transitions(session: Session) -> None:
    """Invalid transitions raise InvalidJobStateTransitionError."""

    org = create_organization(session)
    service = JobService(session)

    # 1. From PLANNED
    job1 = service.create(JobCreate(organization_id=org.id, type="HARROWING"))
    with pytest.raises(InvalidJobStateTransitionError):
        service.pause(job1.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.resume(job1.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.finish(job1.id)

    # 2. From STARTED
    job2 = service.create(JobCreate(organization_id=org.id, type="HARROWING"))
    service.start(job2.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.start(job2.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.resume(job2.id)

    # 3. From PAUSED
    job3 = service.create(JobCreate(organization_id=org.id, type="HARROWING"))
    service.start(job3.id)
    service.pause(job3.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.start(job3.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.pause(job3.id)

    # 4. From COMPLETED (terminal)
    job4 = service.create(JobCreate(organization_id=org.id, type="HARROWING"))
    service.start(job4.id)
    service.finish(job4.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.start(job4.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.pause(job4.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.resume(job4.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.finish(job4.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.cancel(job4.id)

    # 5. From CANCELLED (terminal)
    job5 = service.create(JobCreate(organization_id=org.id, type="HARROWING"))
    service.cancel(job5.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.start(job5.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.pause(job5.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.resume(job5.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.finish(job5.id)
    with pytest.raises(InvalidJobStateTransitionError):
        service.cancel(job5.id)


def test_job_list_all_and_filters(session: Session) -> None:
    """Jobs can be listed with optional filters."""

    org1 = create_organization(session, tax_id="PL-ORG-1")
    org2 = create_organization(session, tax_id="PL-ORG-2")
    m1 = create_machine(session, org1.id, name="Tractor M1")
    u1 = create_operator(session, org1.id, email="op1@example.com")
    service = JobService(session)

    j1 = service.create(
        JobCreate(organization_id=org1.id, machine_id=m1.id, operator_id=u1.id, type="PLOWING")
    )
    j2 = service.create(
        JobCreate(organization_id=org1.id, type="SEEDING")
    )
    service.start(j2.id)

    j3 = service.create(
        JobCreate(organization_id=org2.id, type="HARVESTING")
    )

    all_jobs = service.list_all()
    assert len(all_jobs) == 3

    org1_jobs = service.list_all(organization_id=org1.id)
    assert len(org1_jobs) == 2

    started_jobs = service.list_all(status=JobStatus.STARTED)
    assert len(started_jobs) == 1
    assert started_jobs[0].id == j2.id

    machine_jobs = service.list_all(machine_id=m1.id)
    assert len(machine_jobs) == 1
    assert machine_jobs[0].id == j1.id

    with pytest.raises(OrganizationNotFoundError):
        service.list_all(organization_id=uuid4())

