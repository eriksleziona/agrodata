# Backend

This directory will contain the Python/FastAPI application, Pydantic API
schemas, SQLAlchemy repositories, Alembic migrations, and application services.

No backend implementation or database models are present in the foundation.
Future modules must keep business logic out of route handlers, use UUIDs and UTC
timestamps, and include Pytest coverage for new services.
