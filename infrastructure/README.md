# Infrastructure

## Local development services

`docker-compose.yml` provides the development-only infrastructure stack:

- `postgres`: PostgreSQL 16 with PostGIS 3.4.
- `mosquitto`: MQTT broker.
- `redis`: Redis with append-only persistence.
- `minio`: S3-compatible object storage and its browser console.

Each service has a health check, uses a named persistent volume where it stores
state, and connects to the private `agrodata_internal` Docker network. Required
database and object-storage credentials are supplied only through the ignored
root `.env` file.

The `postgres/init/00-enable-postgis.sql` initialisation script enables the
PostGIS extension on a newly created development database. It does not create
application tables or models. The Mosquitto development configuration permits
anonymous local connections only; production configuration must require
authenticated, encrypted connections.

From the repository root:

```powershell
Copy-Item .env.example .env
# Set POSTGRES_PASSWORD, MINIO_ROOT_USER, and MINIO_ROOT_PASSWORD in .env.
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d
```
