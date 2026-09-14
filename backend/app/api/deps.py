"""FastAPI dependencies for database sessions and authentication."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user import User, UserRole
from app.repositories.users import UserRepository

# ---------------------------------------------------------------------------
# Database session dependency
# ---------------------------------------------------------------------------

DBSessionDep = Annotated[Session, Depends(get_db_session)]

# ---------------------------------------------------------------------------
# Bearer token extraction
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=True)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired authentication credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)

# ---------------------------------------------------------------------------
# RBAC role sets
# ---------------------------------------------------------------------------

#: Roles that are allowed to perform write operations (create / update).
WRITER_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.OPERATOR, UserRole.ADMIN, UserRole.OWNER}
)

#: Roles that are allowed to delete resources.
DELETER_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.OWNER}
)


# ---------------------------------------------------------------------------
# Current user dependency
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    session: Session = Depends(get_db_session),
) -> User:
    """Decode the JWT and return the associated User from the database.

    Raises HTTP 401 if the token is missing, malformed, expired, or the
    referenced user no longer exists.
    """

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise _CREDENTIALS_EXCEPTION

    user_id_str: str | None = payload.get("sub")
    org_id_str: str | None = payload.get("org")

    if not user_id_str or not org_id_str:
        raise _CREDENTIALS_EXCEPTION

    try:
        user_id = UUID(user_id_str)
        org_id = UUID(org_id_str)
    except ValueError:
        raise _CREDENTIALS_EXCEPTION

    user = UserRepository(session).get_by_id(user_id)
    if user is None or user.organization_id != org_id:
        raise _CREDENTIALS_EXCEPTION

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# RBAC guards
# ---------------------------------------------------------------------------


def require_roles(*roles: UserRole):
    """Return a FastAPI dependency that enforces role membership.

    Raises HTTP 403 if the current user's role is not in *roles*.
    """

    role_set = frozenset(roles)

    def _check(current_user: CurrentUserDep) -> User:
        if current_user.role not in role_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This action requires one of the following roles: "
                    f"{', '.join(r.value for r in role_set)}."
                ),
            )
        return current_user

    return Depends(_check)


# ---------------------------------------------------------------------------
# Convenience role-group dependencies
# ---------------------------------------------------------------------------

#: Dependency that passes only OPERATOR, ADMIN, or OWNER users.
RequireWriterDep = require_roles(*WRITER_ROLES)

#: Dependency that passes only ADMIN or OWNER users.
RequireDeleterDep = require_roles(*DELETER_ROLES)
