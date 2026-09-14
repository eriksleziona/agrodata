"""Tests verifying strict cross-organization isolation and RBAC security."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.models.implement import Implement
from app.models.job import Job
from app.models.machine import Machine
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.implement import ImplementCreate
from app.schemas.job import JobCreate
from app.schemas.machine import MachineCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
from app.services.implements import ImplementService
from app.services.jobs import JobService
from app.services.machines import MachineService
from app.services.organizations import OrganizationService
from app.services.users import UserService
from tests.conftest import make_auth_headers


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient bound to the isolated test database session."""

    def override_get_db_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def org_a(session: Session) -> Organization:
    """Create Organization A."""

    return OrganizationService(session).create(
        OrganizationCreate(name="Organization A", tax_id="PL-ORG-A-12345")
    )


@pytest.fixture
def org_b(session: Session) -> Organization:
    """Create Organization B."""

    return OrganizationService(session).create(
        OrganizationCreate(name="Organization B", tax_id="PL-ORG-B-67890")
    )


@pytest.fixture
def user_a_admin(session: Session, org_a: Organization) -> User:
    """Admin user in Organization A."""

    return UserService(session).create(
        UserCreate(
            organization_id=org_a.id,
            email="admin@org-a.com",
            password_hash="hash",
            first_name="Alice",
            last_name="Admin",
            role=UserRole.ADMIN,
        )
    )


@pytest.fixture
def user_a_viewer(session: Session, org_a: Organization) -> User:
    """Viewer user in Organization A."""

    return UserService(session).create(
        UserCreate(
            organization_id=org_a.id,
            email="viewer@org-a.com",
            password_hash="hash",
            first_name="Vic",
            last_name="Viewer",
            role=UserRole.VIEWER,
        )
    )


@pytest.fixture
def user_a_operator(session: Session, org_a: Organization) -> User:
    """Operator user in Organization A."""

    return UserService(session).create(
        UserCreate(
            organization_id=org_a.id,
            email="operator@org-a.com",
            password_hash="hash",
            first_name="Ollie",
            last_name="Operator",
            role=UserRole.OPERATOR,
        )
    )


@pytest.fixture
def user_b_admin(session: Session, org_b: Organization) -> User:
    """Admin user in Organization B."""

    return UserService(session).create(
        UserCreate(
            organization_id=org_b.id,
            email="admin@org-b.com",
            password_hash="hash",
            first_name="Bob",
            last_name="Admin",
            role=UserRole.ADMIN,
        )
    )


@pytest.fixture
def machine_b(session: Session, org_b: Organization) -> Machine:
    """Machine belonging to Organization B."""

    return MachineService(session).create(
        MachineCreate(
            organization_id=org_b.id,
            name="John Deere 8R - Org B",
            device_id="DEV-ORG-B-001",
        )
    )


@pytest.fixture
def implement_b(session: Session, org_b: Organization) -> Implement:
    """Implement belonging to Organization B."""

    return ImplementService(session).create(
        ImplementCreate(
            organization_id=org_b.id,
            name="Kuhn Plow - Org B",
            working_width=4.0,
        )
    )


@pytest.fixture
def job_b(session: Session, org_b: Organization, machine_b: Machine) -> Job:
    """Job belonging to Organization B."""

    return JobService(session).create(
        JobCreate(
            organization_id=org_b.id,
            machine_id=machine_b.id,
            type="HARVESTING",
            area_planned=50.0,
        )
    )


# ---------------------------------------------------------------------------
# Cross-organization access tests (Organization A cannot access Org B data)
# ---------------------------------------------------------------------------


def test_user_a_cannot_read_machine_b(
    client: TestClient,
    user_a_admin: User,
    machine_b: Machine,
) -> None:
    """User from Org A receives 404 when trying to read Machine belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.get(f"/api/v1/machines/{machine_b.id}", headers=headers)
    assert res.status_code == 404


def test_user_a_cannot_update_machine_b(
    client: TestClient,
    user_a_admin: User,
    machine_b: Machine,
) -> None:
    """User from Org A receives 404 when trying to update Machine belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.put(
        f"/api/v1/machines/{machine_b.id}",
        json={"name": "Hacked by Org A"},
        headers=headers,
    )
    assert res.status_code == 404


def test_user_a_cannot_delete_machine_b(
    client: TestClient,
    user_a_admin: User,
    machine_b: Machine,
) -> None:
    """User from Org A receives 404 when trying to delete Machine belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.delete(f"/api/v1/machines/{machine_b.id}", headers=headers)
    assert res.status_code == 404


def test_user_a_cannot_read_implement_b(
    client: TestClient,
    user_a_admin: User,
    implement_b: Implement,
) -> None:
    """User from Org A receives 404 when trying to read Implement belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.get(f"/api/v1/implements/{implement_b.id}", headers=headers)
    assert res.status_code == 404


def test_user_a_cannot_update_implement_b(
    client: TestClient,
    user_a_admin: User,
    implement_b: Implement,
) -> None:
    """User from Org A receives 404 when trying to update Implement belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.put(
        f"/api/v1/implements/{implement_b.id}",
        json={"name": "Hacked by Org A"},
        headers=headers,
    )
    assert res.status_code == 404


def test_user_a_cannot_delete_implement_b(
    client: TestClient,
    user_a_admin: User,
    implement_b: Implement,
) -> None:
    """User from Org A receives 404 when trying to delete Implement belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.delete(f"/api/v1/implements/{implement_b.id}", headers=headers)
    assert res.status_code == 404


def test_user_a_cannot_read_job_b(
    client: TestClient,
    user_a_admin: User,
    job_b: Job,
) -> None:
    """User from Org A receives 404 when trying to read Job belonging to Org B."""

    headers = make_auth_headers(user_a_admin)
    res = client.get(f"/api/v1/jobs/{job_b.id}", headers=headers)
    assert res.status_code == 404


def test_user_a_cannot_trigger_job_b_transitions(
    client: TestClient,
    user_a_admin: User,
    job_b: Job,
) -> None:
    """User from Org A receives 404 when trying to trigger lifecycle transitions on Org B Job."""

    headers = make_auth_headers(user_a_admin)
    assert client.post(f"/api/v1/jobs/{job_b.id}/start", headers=headers).status_code == 404
    assert client.post(f"/api/v1/jobs/{job_b.id}/pause", headers=headers).status_code == 404
    assert client.post(f"/api/v1/jobs/{job_b.id}/resume", headers=headers).status_code == 404
    assert client.post(f"/api/v1/jobs/{job_b.id}/finish", headers=headers).status_code == 404
    assert client.post(f"/api/v1/jobs/{job_b.id}/cancel", headers=headers).status_code == 404


def test_user_a_cannot_attach_org_b_resources_to_job(
    client: TestClient,
    user_a_admin: User,
    org_a: Organization,
    machine_b: Machine,
    implement_b: Implement,
    user_b_admin: User,
) -> None:
    """Creating a job in Org A referencing Org B's machine, implement, or operator is rejected."""

    headers = make_auth_headers(user_a_admin)

    # Org B's machine
    res_mach = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(org_a.id), "type": "SEEDING", "machine_id": str(machine_b.id)},
        headers=headers,
    )
    assert res_mach.status_code == 404

    # Org B's implement
    res_imp = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(org_a.id), "type": "SEEDING", "implement_id": str(implement_b.id)},
        headers=headers,
    )
    assert res_imp.status_code == 404

    # Org B's operator
    res_op = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(org_a.id), "type": "SEEDING", "operator_id": str(user_b_admin.id)},
        headers=headers,
    )
    assert res_op.status_code == 404


def test_list_endpoints_never_leak_cross_org_records(
    client: TestClient,
    user_a_admin: User,
    user_b_admin: User,
    machine_b: Machine,
    implement_b: Implement,
    job_b: Job,
) -> None:
    """Listing machines, implements, or jobs for Org A never returns Org B records."""

    headers_a = make_auth_headers(user_a_admin)
    headers_b = make_auth_headers(user_b_admin)

    # Org A sees empty lists
    assert len(client.get("/api/v1/machines", headers=headers_a).json()) == 0
    assert len(client.get("/api/v1/implements", headers=headers_a).json()) == 0
    assert len(client.get("/api/v1/jobs", headers=headers_a).json()) == 0

    # Org B sees its own records
    assert len(client.get("/api/v1/machines", headers=headers_b).json()) == 1
    assert len(client.get("/api/v1/implements", headers=headers_b).json()) == 1
    assert len(client.get("/api/v1/jobs", headers=headers_b).json()) == 1


# ---------------------------------------------------------------------------
# RBAC Tests (Role-Based Access Control)
# ---------------------------------------------------------------------------


def test_viewer_role_cannot_perform_write_operations(
    client: TestClient,
    user_a_viewer: User,
    org_a: Organization,
) -> None:
    """Users with VIEWER role are forbidden from creating, updating, or deleting resources."""

    headers = make_auth_headers(user_a_viewer)

    # Cannot create machine
    res_create_m = client.post(
        "/api/v1/machines",
        json={"organization_id": str(org_a.id), "name": "Viewer Tractor"},
        headers=headers,
    )
    assert res_create_m.status_code == 403

    # Cannot create implement
    res_create_i = client.post(
        "/api/v1/implements",
        json={"organization_id": str(org_a.id), "name": "Viewer Plow", "working_width": 2.0},
        headers=headers,
    )
    assert res_create_i.status_code == 403

    # Cannot create job
    res_create_j = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(org_a.id), "type": "PLOWING"},
        headers=headers,
    )
    assert res_create_j.status_code == 403


def test_operator_cannot_delete_resources(
    client: TestClient,
    user_a_operator: User,
    user_a_admin: User,
    org_a: Organization,
) -> None:
    """OPERATOR can create and update, but CANNOT delete resources (requires ADMIN/OWNER)."""

    admin_headers = make_auth_headers(user_a_admin)
    operator_headers = make_auth_headers(user_a_operator)

    # Admin creates machine & implement
    m_id = client.post(
        "/api/v1/machines",
        json={"organization_id": str(org_a.id), "name": "Op Test M"},
        headers=admin_headers,
    ).json()["id"]
    i_id = client.post(
        "/api/v1/implements",
        json={"organization_id": str(org_a.id), "name": "Op Test I", "working_width": 3.0},
        headers=admin_headers,
    ).json()["id"]

    # Operator CAN update
    assert client.put(f"/api/v1/machines/{m_id}", json={"name": "Updated M"}, headers=operator_headers).status_code == 200
    assert client.put(f"/api/v1/implements/{i_id}", json={"name": "Updated I"}, headers=operator_headers).status_code == 200

    # Operator CANNOT delete
    assert client.delete(f"/api/v1/machines/{m_id}", headers=operator_headers).status_code == 403
    assert client.delete(f"/api/v1/implements/{i_id}", headers=operator_headers).status_code == 403

    # Admin CAN delete
    assert client.delete(f"/api/v1/machines/{m_id}", headers=admin_headers).status_code == 204
    assert client.delete(f"/api/v1/implements/{i_id}", headers=admin_headers).status_code == 204

