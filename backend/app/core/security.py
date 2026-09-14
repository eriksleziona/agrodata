"""Password hashing and JWT token utilities."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.time import utc_now


def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of *plaintext*."""

    return bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()


def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True if *plaintext* matches *hashed*, False otherwise."""

    return bcrypt.checkpw(plaintext.encode(), hashed.encode())


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
    role: str,
) -> str:
    """Return a signed JWT containing user identity and org claims."""

    settings = get_settings()
    now = utc_now()
    payload = {
        "sub": str(user_id),
        "org": str(organization_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT, raising jwt.PyJWTError on failure."""

    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
