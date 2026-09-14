"""Tests for authentication API endpoints: register, login, and me."""

from __future__ import annotations

from collections.abc import Generator
from datetime import timedelta
from uuid import UUID, uuid4

import bcrypt
from fastapi.testclient import TestClient
import jwt
import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.time import utc_now
from app.db.session import get_db_session
from app.main import app
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.organization import OrganizationCreate
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
    """Create a default organization fixture."""

    return OrganizationService(session).create(
        OrganizationCreate(name="Auth Test Farm", tax_id="PL1112223334")
    )


def test_register_success(client: TestClient, organization: Organization, session: Session) -> None:
    """POST /api/v1/auth/register registers a user, hashes password, never leaks hash."""

    payload = {
        "organization_id": str(organization.id),
        "email": "farmer@authfarm.com",
        "password": "supersecretpassword",
        "first_name": "Adam",
        "last_name": "Nowak",
        "role": "OPERATOR",
    }

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Never return password or password_hash in response
    assert "password" not in data
    assert "password_hash" not in data
    assert data["email"] == "farmer@authfarm.com"
    assert data["role"] == "OPERATOR"
    assert data["first_name"] == "Adam"
    assert data["last_name"] == "Nowak"
    assert data["organization_id"] == str(organization.id)
    assert "id" in data

    # Verify in DB that password is encrypted via bcrypt
    db_user = UserService(session).get_by_id(UUID(data["id"]))
    assert db_user is not None
    assert db_user.password_hash != "supersecretpassword"
    assert bcrypt.checkpw("supersecretpassword".encode(), db_user.password_hash.encode())


def test_register_rejects_unknown_organization(client: TestClient) -> None:
    """POST /api/v1/auth/register returns 404 for non-existent organization."""

    payload = {
        "organization_id": str(uuid4()),
        "email": "orphan@example.com",
        "password": "supersecretpassword",
        "first_name": "Orphan",
        "last_name": "User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_register_rejects_duplicate_email(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/auth/register returns 409 when email already exists in org."""

    payload = {
        "organization_id": str(organization.id),
        "email": "duplicate@authfarm.com",
        "password": "supersecretpassword",
        "first_name": "First",
        "last_name": "User",
    }
    first_res = client.post("/api/v1/auth/register", json=payload)
    assert first_res.status_code == 201

    second_res = client.post("/api/v1/auth/register", json=payload)
    assert second_res.status_code == 409


def test_register_validation_errors(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/auth/register rejects short passwords and invalid emails."""

    # Short password (<8 chars)
    res_short = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": str(organization.id),
            "email": "test@example.com",
            "password": "short",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert res_short.status_code == 422

    # Invalid email
    res_email = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": str(organization.id),
            "email": "not-an-email",
            "password": "supersecretpassword",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert res_email.status_code == 422


def test_login_success(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/auth/login returns valid JWT access token."""

    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": str(organization.id),
            "email": "login_user@authfarm.com",
            "password": "correctpassword123",
            "first_name": "Login",
            "last_name": "Test",
            "role": "ADMIN",
        },
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": str(organization.id),
            "email": "login_user@authfarm.com",
            "password": "correctpassword123",
        },
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Decode and verify token claims
    settings = get_settings()
    claims = jwt.decode(
        token_data["access_token"],
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert claims["org"] == str(organization.id)
    assert claims["role"] == "ADMIN"
    assert "sub" in claims
    assert "exp" in claims


def test_login_invalid_credentials(client: TestClient, organization: Organization) -> None:
    """POST /api/v1/auth/login returns 401 for wrong password, email, or org."""

    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": str(organization.id),
            "email": "user@authfarm.com",
            "password": "correctpassword123",
            "first_name": "User",
            "last_name": "Test",
        },
    )

    # Wrong password
    res_wrong_pw = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": str(organization.id),
            "email": "user@authfarm.com",
            "password": "wrongpassword",
        },
    )
    assert res_wrong_pw.status_code == 401

    # Wrong email
    res_wrong_email = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": str(organization.id),
            "email": "nonexistent@authfarm.com",
            "password": "correctpassword123",
        },
    )
    assert res_wrong_email.status_code == 401

    # Wrong organization ID
    res_wrong_org = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": str(uuid4()),
            "email": "user@authfarm.com",
            "password": "correctpassword123",
        },
    )
    assert res_wrong_org.status_code == 401


def test_get_me_success(client: TestClient, organization: Organization) -> None:
    """GET /api/v1/auth/me returns current user profile and never leaks password_hash."""

    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": str(organization.id),
            "email": "me_user@authfarm.com",
            "password": "correctpassword123",
            "first_name": "Me",
            "last_name": "User",
            "role": "OWNER",
        },
    )
    user_id = reg_res.json()["id"]

    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": str(organization.id),
            "email": "me_user@authfarm.com",
            "password": "correctpassword123",
        },
    )
    token = login_res.json()["access_token"]

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["id"] == user_id
    assert me_data["email"] == "me_user@authfarm.com"
    assert me_data["role"] == "OWNER"
    assert me_data["organization_id"] == str(organization.id)
    assert "password" not in me_data
    assert "password_hash" not in me_data


def test_get_me_unauthorized(client: TestClient) -> None:
    """GET /api/v1/auth/me returns 401 without auth or with invalid/expired token."""

    # Missing header
    res_no_auth = client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401

    # Malformed token
    res_malformed = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert res_malformed.status_code == 401

    # Expired token
    settings = get_settings()
    expired_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "org": str(uuid4()),
            "role": "ADMIN",
            "iat": utc_now() - timedelta(hours=2),
            "exp": utc_now() - timedelta(hours=1),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    res_expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res_expired.status_code == 401
