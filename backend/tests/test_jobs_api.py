"""Tests for Jobs REST API and state transition endpoints."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
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
def organization(session: Session) -> Organization:
    """Create a default organization fixture for API tests."""

    return OrganizationService(session).create(
        OrganizationCreate(name="Job API Farm", tax_id="PL4444444444")
    )


@pytest.fixture
def admin_user(session: Session, organization: Organization) -> User:
    """Create an ADMIN user in the test organization."""

    return UserService(session).create(
        UserCreate(
            organization_id=organization.id,
            email="admin@jobfarm.com",
            password_hash="hash",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )
    )


@pytest.fixture
def headers(admin_user: User) -> dict[str, str]:
    """Return auth headers for the admin user."""

    return make_auth_headers(admin_user)


def test_create_job_success(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/jobs creates a job in PLANNED status."""

    payload = {
        "organization_id": str(organization.id),
        "type": "PLOWING",
        "area_planned": 20.0,
    }

    response = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "PLOWING"
    assert data["status"] == "PLANNED"
    assert data["area_planned"] == 20.0
    assert data["area_completed"] == 0.0
    assert data["organization_id"] == str(organization.id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_job_requires_auth(
    client: TestClient,
    organization: Organization,
) -> None:
    """POST /api/v1/jobs returns 401 when no auth token is provided."""

    response = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "SEEDING"},
    )
    assert response.status_code == 401


def test_create_job_rejects_invalid_inputs(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/jobs returns 422 on bad schema."""

    # Blank type
    res_type = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "   "},
        headers=headers,
    )
    assert res_type.status_code == 422

    # Negative area_planned
    res_area = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "SEEDING", "area_planned": -5.0},
        headers=headers,
    )
    assert res_area.status_code == 422


def test_get_job_by_id(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """GET /api/v1/jobs/{id} returns job details or 404."""

    create_res = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "SPRAYING"},
        headers=headers,
    )
    assert create_res.status_code == 201
    job_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["type"] == "SPRAYING"

    missing_res = client.get(f"/api/v1/jobs/{uuid4()}", headers=headers)
    assert missing_res.status_code == 404


def test_list_jobs_and_filter(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """GET /api/v1/jobs returns list and supports status filtering."""

    j1 = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "JOB1"},
        headers=headers,
    ).json()
    j2 = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "JOB2"},
        headers=headers,
    ).json()

    client.post(f"/api/v1/jobs/{j2['id']}/start", headers=headers)

    all_res = client.get("/api/v1/jobs", headers=headers)
    assert all_res.status_code == 200
    assert len(all_res.json()) == 2

    planned_res = client.get("/api/v1/jobs?status=PLANNED", headers=headers)
    assert planned_res.status_code == 200
    assert len(planned_res.json()) == 1
    assert planned_res.json()[0]["id"] == j1["id"]

    started_res = client.get("/api/v1/jobs?status=STARTED", headers=headers)
    assert started_res.status_code == 200
    assert len(started_res.json()) == 1
    assert started_res.json()[0]["id"] == j2["id"]


def test_job_state_transition_lifecycle_api(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """API endpoints transition jobs correctly across lifecycle."""

    create_res = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "HARVESTING"},
        headers=headers,
    )
    job_id = create_res.json()["id"]

    # 1. Start job
    start_res = client.post(f"/api/v1/jobs/{job_id}/start", headers=headers)
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "STARTED"
    assert start_res.json()["started_at"] is not None

    # Starting already started job returns 409 Conflict
    conflict_start = client.post(f"/api/v1/jobs/{job_id}/start", headers=headers)
    assert conflict_start.status_code == 409

    # 2. Pause job
    pause_res = client.post(f"/api/v1/jobs/{job_id}/pause", headers=headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    # Pausing already paused job returns 409 Conflict
    conflict_pause = client.post(f"/api/v1/jobs/{job_id}/pause", headers=headers)
    assert conflict_pause.status_code == 409

    # 3. Resume job
    resume_res = client.post(f"/api/v1/jobs/{job_id}/resume", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "STARTED"

    # 4. Finish job with metrics
    finish_res = client.post(
        f"/api/v1/jobs/{job_id}/finish",
        json={
            "area_completed": 18.2,
            "distance": 12000.0,
            "working_time": 7200,
            "idle_time": 600,
            "fuel_used": 45.0,
        },
        headers=headers,
    )
    assert finish_res.status_code == 200
    data = finish_res.json()
    assert data["status"] == "COMPLETED"
    assert data["finished_at"] is not None
    assert data["area_completed"] == 18.2
    assert data["distance"] == 12000.0
    assert data["working_time"] == 7200
    assert data["idle_time"] == 600
    assert data["fuel_used"] == 45.0

    # Operating on finished job returns 409 Conflict
    assert client.post(f"/api/v1/jobs/{job_id}/start", headers=headers).status_code == 409
    assert client.post(f"/api/v1/jobs/{job_id}/pause", headers=headers).status_code == 409
    assert client.post(f"/api/v1/jobs/{job_id}/resume", headers=headers).status_code == 409
    assert client.post(f"/api/v1/jobs/{job_id}/finish", headers=headers).status_code == 409
    assert client.post(f"/api/v1/jobs/{job_id}/cancel", headers=headers).status_code == 409


def test_job_cancel_api(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/jobs/{id}/cancel transitions job to CANCELLED."""

    create_res = client.post(
        "/api/v1/jobs",
        json={"organization_id": str(organization.id), "type": "TILLAGE"},
        headers=headers,
    )
    job_id = create_res.json()["id"]

    cancel_res = client.post(f"/api/v1/jobs/{job_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
    assert cancel_res.json()["finished_at"] is not None

    # Cancelling again returns 409 Conflict
    assert client.post(f"/api/v1/jobs/{job_id}/cancel", headers=headers).status_code == 409
