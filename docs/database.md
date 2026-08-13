# Database setup

## Scope

The current database foundation provides PostgreSQL/PostGIS configuration,
SQLAlchemy connection and session management, Alembic migrations, and a
non-sensitive connectivity health check. It deliberately contains no business
models, application tables, or domain repositories.

## Prerequisites

- Python 3.12 or later.
- Docker Desktop running locally for PostgreSQL/PostGIS.
- A local `.env` copied from `.env.example` with a non-empty
  `POSTGRES_PASSWORD`.

## Configuration

The backend reads environment variables and, for local development, the root
`.env` file. Environment variables take precedence over file values.

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | Optional complete PostgreSQL URL. Takes precedence over individual values. | None |
| `POSTGRES_HOST` | PostgreSQL host. | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port. | `5432` |
| `POSTGRES_DB` | Database name. | `agrodata` |
| `POSTGRES_USER` | Database user. | `agrodata` |
| `POSTGRES_PASSWORD` | Database password. Keep only in local environment configuration or secret storage. | None |
| `DATABASE_POOL_SIZE` | SQLAlchemy steady-state pool size. | `5` |
| `DATABASE_MAX_OVERFLOW` | Additional temporary pooled connections. | `10` |

For a backend container on the Compose network, use `POSTGRES_HOST=postgres`.
Do not put real URLs or credentials in tracked files.

## Local setup

From the repository root:

```powershell
Copy-Item .env.example .env
# Set POSTGRES_PASSWORD, MINIO_ROOT_USER, and MINIO_ROOT_PASSWORD in .env.
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d --wait

py -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e .\backend[dev]
```

Apply the initial migration after PostgreSQL is healthy:

```powershell
.\.venv\Scripts\alembic -c backend/alembic.ini upgrade head
```

The migration creates the `postgis` extension with `CREATE EXTENSION IF NOT
EXISTS postgis`. The Docker initialisation script performs the same idempotent
operation for a newly created local volume, so either ordering is safe.

## Session management

`app.db.session` exposes:

- `get_engine()` for the process-wide SQLAlchemy engine.
- `get_session_factory()` for creating short-lived sessions.
- `get_db_session()` as a generator dependency for a future API layer. It closes
  every session and rolls back work when an exception escapes.

Database operations must use a short-lived session per unit of work. Future
route handlers must not contain persistence or business logic directly.

## Health check

`app.db.health.check_database_connection(engine)` runs `SELECT 1` and returns a
UTC-stamped `DatabaseHealth` result. Failures expose only an exception class
name, never credentials or a connection URL. A future HTTP health endpoint can
adapt this service without coupling database code to FastAPI.

## Timestamp policy

All future persisted timestamps must be timezone-aware UTC values. Use
`DateTime(timezone=True)` in SQLAlchemy models and `app.core.time.utc_now()` for
application-generated timestamps. API boundaries must serialise timestamps as
ISO 8601 values.

## Tests

Run unit tests without a PostgreSQL server:

```powershell
.\.venv\Scripts\python -m pytest backend/tests -m "not integration"
```

To run the PostgreSQL/PostGIS connectivity test, set
`AGRODATA_TEST_DATABASE_URL` to a local development database URL in your shell
or secure test runner configuration, then run:

```powershell
.\.venv\Scripts\python -m pytest backend/tests -m integration
```

The integration test verifies both a database connection and that the `postgis`
extension is available.
