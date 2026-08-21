"""Tests for Implements REST API endpoints."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate
from app.services.organizations import OrganizationService


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
        OrganizationCreate(name="Implement Farm", tax_id="PL7777777777")
    )


def test_create_implement_success(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/implements creates an implement with all properties."""

    payload = {
        "organization_id": str(organization.id),
        "name": "Amazone UX 11200",
        "manufacturer": "Amazone",
        "model": "UX 11200",
        "type": "SPRAYER",
        "working_width": 36.0,
    }

    response = client.post("/api/v1/implements", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Amazone UX 11200"
    assert data["manufacturer"] == "Amazone"
    assert data["model"] == "UX 11200"
    assert data["type"] == "SPRAYER"
    assert data["working_width"] == 36.0
    assert data["organization_id"] == str(organization.id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_implement_rejects_missing_organization(client: TestClient) -> None:
    """POST /api/v1/implements returns 404 when organization_id does not exist."""

    payload = {
        "organization_id": str(uuid4()),
        "name": "Orphan Implement",
        "working_width": 4.0,
    }

    response = client.post("/api/v1/implements", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_implement_validation_errors(
    client: TestClient,
    organization: Organization,
) -> None:
    """POST /api/v1/implements returns 422 on invalid input."""

    # Zero working_width
    response = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Harrow",
            "working_width": 0.0,
        },
    )
    assert response.status_code == 422

    # Negative working_width
    response = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Harrow",
            "working_width": -3.0,
        },
    )
    assert response.status_code == 422

    # Blank name
    response = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "   ",
            "working_width": 3.0,
        },
    )
    assert response.status_code == 422


def test_get_implement_by_id(client: TestClient, organization: Organization) -> None:
    """GET /api/v1/implements/{id} returns the implement details or 404."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Plow 1",
            "working_width": 2.5,
        },
    )
    assert create_res.status_code == 201
    implement_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/implements/{implement_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Plow 1"
    assert get_res.json()["working_width"] == 2.5

    missing_res = client.get(f"/api/v1/implements/{uuid4()}")
    assert missing_res.status_code == 404


def test_list_implements(
    client: TestClient,
    organization: Organization,
    session: Session,
) -> None:
    """GET /api/v1/implements returns list of implements and supports filtering."""

    org2 = OrganizationService(session).create(
        OrganizationCreate(name="Second Farm", tax_id="PL8888888888")
    )

    client.post(
        "/api/v1/implements",
        json={"organization_id": str(organization.id), "name": "Imp 1", "working_width": 3.0},
    )
    client.post(
        "/api/v1/implements",
        json={"organization_id": str(organization.id), "name": "Imp 2", "working_width": 6.0},
    )
    client.post(
        "/api/v1/implements",
        json={"organization_id": str(org2.id), "name": "Imp 3", "working_width": 9.0},
    )

    all_res = client.get("/api/v1/implements")
    assert all_res.status_code == 200
    assert len(all_res.json()) == 3

    filtered_res = client.get(f"/api/v1/implements?organization_id={organization.id}")
    assert filtered_res.status_code == 200
    assert len(filtered_res.json()) == 2
    assert {i["name"] for i in filtered_res.json()} == {"Imp 1", "Imp 2"}


def test_update_implement(client: TestClient, organization: Organization) -> None:
    """PUT /api/v1/implements/{id} updates implement attributes and validates width."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Old Seeder",
            "working_width": 3.0,
        },
    )
    implement_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/implements/{implement_id}",
        json={"name": "New Seeder", "working_width": 4.5},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Seeder"
    assert update_res.json()["working_width"] == 4.5

    # Invalid working width update
    invalid_update_res = client.put(
        f"/api/v1/implements/{implement_id}",
        json={"working_width": 0.0},
    )
    assert invalid_update_res.status_code == 422

    missing_res = client.put(
        f"/api/v1/implements/{uuid4()}",
        json={"name": "Ghost"},
    )
    assert missing_res.status_code == 404


def test_delete_implement(client: TestClient, organization: Organization) -> None:
    """DELETE /api/v1/implements/{id} deletes the implement and returns 204."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "ToDelete",
            "working_width": 1.5,
        },
    )
    implement_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/implements/{implement_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/implements/{implement_id}")
    assert get_res.status_code == 404

    del_missing = client.delete(f"/api/v1/implements/{uuid4()}")
    assert del_missing.status_code == 404

