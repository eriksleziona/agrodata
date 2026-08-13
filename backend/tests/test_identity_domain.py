"""Tests for Organization and User domain persistence services."""

from datetime import UTC
from uuid import UUID, uuid4

import pytest
from sqlalchemy import UniqueConstraint, inspect
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.schemas.user import UserCreate, UserRead
from app.services.errors import DuplicateUserEmailError, OrganizationNotFoundError
from app.services.organizations import OrganizationService
from app.services.users import UserService


def create_organization(session: Session, tax_id: str = "PL1234567890") -> Organization:
    """Create an organization fixture through its application service."""

    return OrganizationService(session).create(
        OrganizationCreate(name="Green Fields", tax_id=tax_id)
    )


def test_organization_service_persists_uuid_and_utc_timestamp_columns(
    session: Session,
) -> None:
    """Organizations use UUID keys and timezone-aware UTC timestamp fields."""

    organization = create_organization(session)

    assert isinstance(organization.id, UUID)
    assert organization.name == "Green Fields"
    assert organization.tax_id == "PL1234567890"
    assert inspect(Organization).columns.created_at.type.timezone is True
    assert inspect(Organization).columns.updated_at.type.timezone is True
    assert Organization.__table__.c.created_at.default.is_callable
    assert Organization.__table__.c.updated_at.default.is_callable
    assert utc_now().tzinfo is UTC

    response = OrganizationRead.model_validate(organization)
    assert response.id == organization.id


@pytest.mark.parametrize("role", list(UserRole))
def test_user_service_persists_each_supported_role(
    session: Session,
    role: UserRole,
) -> None:
    """Users are created with all explicitly supported organization roles."""

    organization = create_organization(session, tax_id=f"PL-{role.value}")
    user = UserService(session).create(
        UserCreate(
            organization_id=organization.id,
            email=f"{role.value.lower()}@example.test",
            password_hash="opaque-password-hash",
            first_name="Ada",
            last_name="Farmer",
            role=role,
        )
    )

    assert isinstance(user.id, UUID)
    assert user.organization_id == organization.id
    assert user.role is role
    assert inspect(User).columns.created_at.type.timezone is True
    assert inspect(User).columns.updated_at.type.timezone is True

    response = UserRead.model_validate(user)
    assert response.role is role
    assert "password_hash" not in response.model_dump()


def test_user_email_is_unique_per_organization_and_normalized(
    session: Session,
) -> None:
    """The same email can exist across organizations but not within one."""

    first_organization = create_organization(session, tax_id="PL1111111111")
    second_organization = create_organization(session, tax_id="PL2222222222")
    service = UserService(session)

    service.create(
        UserCreate(
            organization_id=first_organization.id,
            email="Farmer@Example.Test ",
            password_hash="opaque-password-hash",
            first_name="Ada",
            last_name="Farmer",
            role=UserRole.FARMER,
        )
    )
    second_user = service.create(
        UserCreate(
            organization_id=second_organization.id,
            email="farmer@example.test",
            password_hash="opaque-password-hash",
            first_name="Bea",
            last_name="Operator",
            role=UserRole.OPERATOR,
        )
    )

    with pytest.raises(DuplicateUserEmailError):
        service.create(
            UserCreate(
                organization_id=first_organization.id,
                email="farmer@example.test",
                password_hash="opaque-password-hash",
                first_name="Cara",
                last_name="Viewer",
                role=UserRole.VIEWER,
            )
        )

    assert second_user.email == "farmer@example.test"


def test_user_service_rejects_an_unknown_organization(session: Session) -> None:
    """User creation is constrained to an existing organization."""

    with pytest.raises(OrganizationNotFoundError):
        UserService(session).create(
            UserCreate(
                organization_id=uuid4(),
                email="missing@example.test",
                password_hash="opaque-password-hash",
                first_name="Dana",
                last_name="Farmer",
                role=UserRole.FARMER,
            )
        )


def test_models_declare_the_required_indexes_and_unique_constraint() -> None:
    """Identity persistence exposes the required query and integrity indexes."""

    organization_indexes = {index.name for index in Organization.__table__.indexes}
    user_indexes = {index.name for index in User.__table__.indexes}
    unique_constraints = {
        constraint.name
        for constraint in User.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert "ix_organizations_tax_id" in organization_indexes
    assert "ix_users_organization_id" in user_indexes
    assert "uq_users_organization_id_email" in unique_constraints
