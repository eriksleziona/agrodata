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
        OrganizationCreate(name="Implement Farm", tax_id="PL7777777777")
    )


@pytest.fixture
def admin_user(session: Session, organization: Organization) -> User:
    """Create an ADMIN user in the test organization."""

    return UserService(session).create(
        UserCreate(
            organization_id=organization.id,
            email="admin@implementfarm.com",
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


def test_create_implement_success(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """POST /api/v1/implements creates an implement with all properties."""

    payload = {
        "organization_id": str(organization.id),
        "name": "Amazone UX 11200",
        "manufacturer": "Amazone",
        "model": "UX 11200",
        "type": "SPRAYER",
        "working_width": 36.0,
    }

    response = client.post("/api/v1/implements", json=payload, headers=headers)
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


def test_create_implement_requires_auth(
    client: TestClient,
    organization: Organization,
) -> None:
    """POST /api/v1/implements returns 401 when no auth token is provided."""

    response = client.post(
        "/api/v1/implements",
        json={"organization_id": str(organization.id), "name": "Ghost", "working_width": 2.0},
    )
    assert response.status_code == 401


def test_create_implement_rejects_missing_organization(
    client: TestClient,
) -> None:
    """POST /api/v1/implements returns 401 when auth token references non-existent user/org."""

    import jwt as pyjwt
    from datetime import timedelta
    from app.core.config import get_settings
    from app.core.time import utc_now

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
        "/api/v1/implements",
        json={"name": "Orphan Implement", "working_width": 4.0},
        headers={"Authorization": f"Bearer {fake_token}"},
    )
    assert response.status_code == 401


def test_create_implement_validation_errors(
    client: TestClient,
    organization: Organization,
    headers: dict,
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
        headers=headers,
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
        headers=headers,
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
        headers=headers,
    )
    assert response.status_code == 422


def test_get_implement_by_id(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """GET /api/v1/implements/{id} returns the implement details or 404."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Plow 1",
            "working_width": 2.5,
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    implement_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/implements/{implement_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Plow 1"
    assert get_res.json()["working_width"] == 2.5

    missing_res = client.get(f"/api/v1/implements/{uuid4()}", headers=headers)
    assert missing_res.status_code == 404


def test_list_implements(
    client: TestClient,
    organization: Organization,
    headers: dict,
    session: Session,
) -> None:
    """GET /api/v1/implements returns list of implements scoped to current org."""

    org2 = OrganizationService(session).create(
        OrganizationCreate(name="Second Farm", tax_id="PL8888888888")
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

    client.post(
        "/api/v1/implements",
        json={"organization_id": str(organization.id), "name": "Imp 1", "working_width": 3.0},
        headers=headers,
    )
    client.post(
        "/api/v1/implements",
        json={"organization_id": str(organization.id), "name": "Imp 2", "working_width": 6.0},
        headers=headers,
    )
    client.post(
        "/api/v1/implements",
        json={"organization_id": str(org2.id), "name": "Imp 3", "working_width": 9.0},
        headers=headers2,
    )

    # Org1 user sees only org1 implements
    res1 = client.get("/api/v1/implements", headers=headers)
    assert res1.status_code == 200
    assert len(res1.json()) == 2
    assert {i["name"] for i in res1.json()} == {"Imp 1", "Imp 2"}

    # Org2 user sees only org2 implements
    res2 = client.get("/api/v1/implements", headers=headers2)
    assert res2.status_code == 200
    assert len(res2.json()) == 1
    assert res2.json()[0]["name"] == "Imp 3"


def test_update_implement(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """PUT /api/v1/implements/{id} updates implement attributes and validates width."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "Old Seeder",
            "working_width": 3.0,
        },
        headers=headers,
    )
    implement_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/implements/{implement_id}",
        json={"name": "New Seeder", "working_width": 4.5},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Seeder"
    assert update_res.json()["working_width"] == 4.5

    # Invalid working width update
    invalid_update_res = client.put(
        f"/api/v1/implements/{implement_id}",
        json={"working_width": 0.0},
        headers=headers,
    )
    assert invalid_update_res.status_code == 422

    missing_res = client.put(
        f"/api/v1/implements/{uuid4()}",
        json={"name": "Ghost"},
        headers=headers,
    )
    assert missing_res.status_code == 404


def test_delete_implement(
    client: TestClient,
    organization: Organization,
    headers: dict,
) -> None:
    """DELETE /api/v1/implements/{id} deletes the implement and returns 204."""

    create_res = client.post(
        "/api/v1/implements",
        json={
            "organization_id": str(organization.id),
            "name": "ToDelete",
            "working_width": 1.5,
        },
        headers=headers,
    )
    implement_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/implements/{implement_id}", headers=headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/implements/{implement_id}", headers=headers)
    assert get_res.status_code == 404

    del_missing = client.delete(f"/api/v1/implements/{uuid4()}", headers=headers)
    assert del_missing.status_code == 404
