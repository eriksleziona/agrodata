"""Tests for Machines REST API endpoints."""

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
        OrganizationCreate(name="API Test Farm", tax_id="PL5555555555")
    )


def test_create_machine_success(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/machines creates a machine with all properties."""

    payload = {
        "organization_id": str(organization.id),
        "name": "Claas Lexion 8900",
        "manufacturer": "Claas",
        "model": "Lexion 8900",
        "serial_number": "C8900-12345",
        "year": 2023,
        "power_hp": 790,
        "device_id": "EDGE-BOX-999",
    }

    response = client.post("/api/v1/machines", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Claas Lexion 8900"
    assert data["manufacturer"] == "Claas"
    assert data["model"] == "Lexion 8900"
    assert data["serial_number"] == "C8900-12345"
    assert data["year"] == 2023
    assert data["power_hp"] == 790
    assert data["device_id"] == "EDGE-BOX-999"
    assert data["organization_id"] == str(organization.id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_machine_rejects_missing_organization(client: TestClient) -> None:
    """POST /api/v1/machines returns 404 when organization_id does not exist."""

    payload = {
        "organization_id": str(uuid4()),
        "name": "Orphan Tractor",
    }

    response = client.post("/api/v1/machines", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_machine_rejects_duplicate_device_id(
    client: TestClient,
    organization: Organization,
) -> None:
    """POST /api/v1/machines returns 409 Conflict when device_id is duplicated."""

    payload = {
        "organization_id": str(organization.id),
        "name": "Tractor 1",
        "device_id": "SHARED-DEV-ID",
    }
    first_res = client.post("/api/v1/machines", json=payload)
    assert first_res.status_code == 201

    payload2 = {
        "organization_id": str(organization.id),
        "name": "Tractor 2",
        "device_id": "SHARED-DEV-ID",
    }
    second_res = client.post("/api/v1/machines", json=payload2)
    assert second_res.status_code == 409
    assert "already exists" in second_res.json()["detail"]


def test_create_machine_validation_errors(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/machines returns 422 on invalid input."""

    # Blank name
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "   "},
    )
    assert response.status_code == 422

    # Negative power
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Tractor", "power_hp": -10},
    )
    assert response.status_code == 422

    # Invalid year
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Tractor", "year": 1850},
    )
    assert response.status_code == 422


def test_get_machine_by_id(client: TestClient, organization: Organization) -> None:
    """GET /api/v1/machines/{id} returns the machine details or 404."""

    create_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Valtra T235"},
    )
    assert create_res.status_code == 201
    machine_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/machines/{machine_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Valtra T235"

    missing_res = client.get(f"/api/v1/machines/{uuid4()}")
    assert missing_res.status_code == 404


def test_list_machines(client: TestClient, organization: Organization, session: Session) -> None:
    """GET /api/v1/machines returns list of machines and supports filtering."""

    org2 = OrganizationService(session).create(
        OrganizationCreate(name="Second Farm", tax_id="PL6666666666")
    )

    client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "M1"})
    client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "M2"})
    client.post("/api/v1/machines", json={"organization_id": str(org2.id), "name": "M3"})

    all_res = client.get("/api/v1/machines")
    assert all_res.status_code == 200
    assert len(all_res.json()) == 3

    filtered_res = client.get(f"/api/v1/machines?organization_id={organization.id}")
    assert filtered_res.status_code == 200
    assert len(filtered_res.json()) == 2
    assert {m["name"] for m in filtered_res.json()} == {"M1", "M2"}


def test_update_machine(client: TestClient, organization: Organization) -> None:
    """PUT /api/v1/machines/{id} updates machine attributes."""

    create_res = client.post(
        "/api/v1/machines",
        json={
            "organization_id": str(organization.id),
            "name": "Old Name",
            "power_hp": 150,
            "device_id": "OLD-DEV-1",
        },
    )
    machine_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/machines/{machine_id}",
        json={"name": "New Name", "power_hp": 180},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"
    assert update_res.json()["power_hp"] == 180
    assert update_res.json()["device_id"] == "OLD-DEV-1"

    missing_res = client.put(
        f"/api/v1/machines/{uuid4()}",
        json={"name": "Ghost"},
    )
    assert missing_res.status_code == 404


def test_update_machine_rejects_conflicting_device_id(
    client: TestClient,
    organization: Organization,
) -> None:
    """PUT /api/v1/machines/{id} returns 409 Conflict when updating to taken device_id."""

    m1_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "T1", "device_id": "DEV-1"},
    )
    m2_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "T2", "device_id": "DEV-2"},
    )

    conflict_res = client.put(
        f"/api/v1/machines/{m1_res.json()['id']}",
        json={"device_id": "DEV-2"},
    )
    assert conflict_res.status_code == 409


def test_delete_machine(client: TestClient, organization: Organization) -> None:
    """DELETE /api/v1/machines/{id} deletes the machine and returns 204."""

    create_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "ToDelete"},
    )
    machine_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/machines/{machine_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/machines/{machine_id}")
    assert get_res.status_code == 404

    del_missing = client.delete(f"/api/v1/machines/{uuid4()}")
    assert del_missing.status_code == 404

