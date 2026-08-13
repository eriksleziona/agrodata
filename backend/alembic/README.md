# Alembic migrations

Alembic owns database schema changes. Create a new revision for every schema
change and apply it with `alembic -c backend/alembic.ini upgrade head`.

The first revision enables PostGIS only. It deliberately creates no application
tables or business models.
