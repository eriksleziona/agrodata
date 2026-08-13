"""Environment-based application configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, make_url


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Settings shared by backend infrastructure components.

    A full ``DATABASE_URL`` takes precedence over individual ``POSTGRES_*``
    values, which keeps container, test, and hosted environments configurable
    without source changes.
    """

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    agrodata_env: Literal["development", "test", "production"] = "development"
    database_url_override: str | None = Field(
        default=None,
        validation_alias="DATABASE_URL",
    )
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "agrodata"
    postgres_user: str = "agrodata"
    postgres_password: SecretStr = SecretStr("")
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)

    @property
    def database_url(self) -> URL:
        """Return a SQLAlchemy PostgreSQL URL without exposing secrets in logs."""

        if self.database_url_override:
            url = make_url(self.database_url_override)
            if url.get_backend_name() != "postgresql":
                message = "DATABASE_URL must use a PostgreSQL dialect."
                raise ValueError(message)
            if url.drivername == "postgresql":
                return url.set(drivername="postgresql+psycopg")
            return url

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""

    return Settings()
