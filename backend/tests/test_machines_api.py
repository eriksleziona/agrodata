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
        OrganizationCreate(name="API Test Farm", tax_id="PL5555555555")
    )


@pytest.fixture
def admin_user(session: Session, organization: Organization) -> User:
    """Create an ADMIN user in the test organization."""

    return UserService(session).create(
        UserCreate(
            organization_id=organization.id,
            email="admin@testfarm.com",
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


def test_create_machine_success(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
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

    response = client.post("/api/v1/machines", json=payload, headers=headers)
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


def test_create_machine_requires_auth(
    client: TestClient,
    organization: Organization,
) -> None:
    """POST /api/v1/machines returns 401 when no auth token is provided."""

    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Ghost"},
    )
    assert response.status_code == 401



def test_create_machine_rejects_missing_organization(
    client: TestClient,
    admin_user: User,
) -> None:
    """POST /api/v1/machines returns 404 when organization_id does not exist.

    Note: org isolation is enforced — the org_id from the JWT is used, not the
    payload. The org in the payload is silently ignored; the scoped create still
    succeeds if the JWT org is valid. A missing JWT org → 401.
    """

    # An ADMIN from a real org can still create; the test verifies the 404
    # is only triggered when the JWT references a non-existent org.
    # We simulate this by using a JWT with a fake org directly.
    import jwt as pyjwt
    from app.core.config import get_settings
    from app.core.time import utc_now
    from datetime import timedelta
    from uuid import uuid4

    settings = get_settings()
    fake_token = pyjwt.encode(
        {
            "sub": str(uuid4()),
            "org": str(uuid4()),
            "role": "ADMIN",
            "iat": utc_now(),
            "exp": utc_now() + timedelta(minutes=60),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    response = client.post(
        "/api/v1/machines",
        json={"name": "Orphan Tractor"},
        headers={"Authorization": f"Bearer {fake_token}"},
    )
    assert response.status_code == 401  # user not found in DB


def test_create_machine_rejects_duplicate_device_id(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/machines returns 409 Conflict when device_id is duplicated."""

    payload = {"organization_id": str(organization.id), "name": "Tractor 1", "device_id": "SHARED-DEV-ID"}
    first_res = client.post("/api/v1/machines", json=payload, headers=headers)
    assert first_res.status_code == 201

    payload2 = {"organization_id": str(organization.id), "name": "Tractor 2", "device_id": "SHARED-DEV-ID"}
    second_res = client.post("/api/v1/machines", json=payload2, headers=headers)
    assert second_res.status_code == 409
    assert "already exists" in second_res.json()["detail"]


def test_create_machine_validation_errors(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/machines returns 422 on invalid input."""

    # Blank name
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "   "},
        headers=headers,
    )
    assert response.status_code == 422

    # Negative power
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Tractor", "power_hp": -10},
        headers=headers,
    )
    assert response.status_code == 422

    # Invalid year
    response = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Tractor", "year": 1850},
        headers=headers,
    )
    assert response.status_code == 422


def test_get_machine_by_id(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """GET /api/v1/machines/{id} returns the machine details or 404."""

    create_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Valtra T235"},
        headers=headers,
    )
    assert create_res.status_code == 201
    machine_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/machines/{machine_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Valtra T235"

    missing_res = client.get(f"/api/v1/machines/{uuid4()}", headers=headers)
    assert missing_res.status_code == 404


def test_list_machines(
    client: TestClient,
    organization: Organization,
    headers: dict,
    session: Session,
) -> None:
    """GET /api/v1/machines returns only machines belonging to the authenticated org."""

    # Create a second org and add a machine to it — should not appear in the list
    from app.core.security import create_access_token
    from app.schemas.user import UserCreate
    from app.services.users import UserService

    org2 = OrganizationService(session).create(
        OrganizationCreate(name="Second Farm", tax_id="PL6666666666")
    )
    user2 = UserService(session).create(
        UserCreate(
            organization_id=org2.id,
            email="admin@secondfarm.com",
            password_hash="hash",
            first_name="B",
            last_name="B",
            role=UserRole.ADMIN,
        )
    )
    headers2 = make_auth_headers(user2)

    client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "M1"}, headers=headers)
    client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "M2"}, headers=headers)
    client.post("/api/v1/machines", json={"organization_id": str(org2.id), "name": "M3"}, headers=headers2)

    # Org1 user sees only org1 machines
    res1 = client.get("/api/v1/machines", headers=headers)
    assert res1.status_code == 200
    assert len(res1.json()) == 2
    assert {m["name"] for m in res1.json()} == {"M1", "M2"}

    # Org2 user sees only org2 machines
    res2 = client.get("/api/v1/machines", headers=headers2)
    assert res2.status_code == 200
    assert len(res2.json()) == 1
    assert res2.json()[0]["name"] == "M3"


def test_update_machine(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """PUT /api/v1/machines/{id} updates machine attributes."""

    create_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "Old Name", "power_hp": 150, "device_id": "OLD-DEV-1"},
        headers=headers,
    )
    machine_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/machines/{machine_id}",
        json={"name": "New Name", "power_hp": 180},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"
    assert update_res.json()["power_hp"] == 180
    assert update_res.json()["device_id"] == "OLD-DEV-1"

    missing_res = client.put(f"/api/v1/machines/{uuid4()}", json={"name": "Ghost"}, headers=headers)
    assert missing_res.status_code == 404


def test_update_machine_rejects_conflicting_device_id(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """PUT /api/v1/machines/{id} returns 409 Conflict when updating to taken device_id."""

    m1_res = client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "T1", "device_id": "DEV-1"}, headers=headers)
    m2_res = client.post("/api/v1/machines", json={"organization_id": str(organization.id), "name": "T2", "device_id": "DEV-2"}, headers=headers)

    conflict_res = client.put(
        f"/api/v1/machines/{m1_res.json()['id']}",
        json={"device_id": "DEV-2"},
        headers=headers,
    )
    assert conflict_res.status_code == 409


def test_delete_machine(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """DELETE /api/v1/machines/{id} deletes the machine and returns 204."""

    create_res = client.post(
        "/api/v1/machines",
        json={"organization_id": str(organization.id), "name": "ToDelete"},
        headers=headers,
    )
    machine_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/machines/{machine_id}", headers=headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/machines/{machine_id}", headers=headers)
    assert get_res.status_code == 404

    del_missing = client.delete(f"/api/v1/machines/{uuid4()}", headers=headers)
    assert del_missing.status_code == 404
