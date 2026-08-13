# Backend

This directory contains the Python backend foundation: environment-based
configuration, synchronous SQLAlchemy session management, Alembic migrations,
and database connectivity health checks. It will later contain the FastAPI
application, Pydantic API schemas, repositories, and application services.

The initial Alembic revisions enable PostGIS and establish Organization/User
persistence only. Authentication and API routes do not exist yet. Future modules
must keep business logic out of route handlers, use UUIDs and UTC timestamps,
and include Pytest coverage for new services.

See [database setup](../docs/database.md) for installation, migrations, tests,
and configuration guidance.
See [identity foundation](../docs/identity.md) for the Organization/User model,
roles, and current scope.
