# AgroData

AgroData is a planned precision-agriculture platform for farm management, GIS,
GNSS/RTK, machine telemetry, IoT sensors, jobs, field coverage, satellite
imagery, weather, analytics, reporting, and future AI-assisted workflows.

## Project status

This repository currently contains the initial project foundation and local
development dependencies. It has no business logic, API routes, database
models, migrations, or application services yet.

## Target architecture

```text
React + TypeScript frontend
            |
         FastAPI
            |
PostgreSQL/PostGIS  Redis  MQTT  S3-compatible storage
            |
  Edge devices, GNSS/RTK, sensors, and machine telemetry
```

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand,
  and MapLibre.
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, and Alembic.
- **Data and messaging:** PostgreSQL/PostGIS, Redis, MQTT/Mosquitto, and
  S3-compatible storage such as MinIO.
- **Delivery and validation:** Docker, Docker Compose, Nginx, Pytest, Vitest,
  and Playwright.

## Modules

| Directory | Responsibility |
| --- | --- |
| `backend/` | API, application services, repositories, and migrations. |
| `frontend/` | Web application and map-based user interface. |
| `edge/` | Edge-agent integration with GNSS, sensors, CAN, and offline storage. |
| `firmware/` | Firmware for supported field devices. |
| `simulator/` | Simulated devices and agricultural data sources. |
| `gis/` | Spatial-data conventions, processing, and reference material. |
| `satellite/` | Satellite imagery integrations and processing. |
| `analytics/` | Analytics pipelines, reporting, and future AI work. |
| `infrastructure/` | Container, proxy, and deployment configuration. |
| `docs/` | Architecture and operational documentation. |
| `tests/` | Cross-module integration and end-to-end tests. |

## Development workflow

1. Copy `.env.example` to a local `.env` file and enter values only on your
   machine. Keep credentials out of source control.
2. Make schema changes through Alembic migrations once the backend foundation is
   introduced; never edit deployed databases manually.
3. Put business rules in backend services, persistence access in repositories,
   and keep API route handlers thin.
4. Use UUID identifiers and UTC timestamps. Expose timestamps as ISO 8601 in
   APIs and use PostGIS for spatial data.
5. Add documentation and automated tests alongside every new feature.

## Local development infrastructure

Development services are defined in `infrastructure/docker-compose.yml`. The
configuration uses a dedicated Compose project, named persistent volumes, and
one internal Docker network. It starts PostgreSQL with PostGIS, Mosquitto, Redis,
and MinIO; no application code is included.

Before starting the stack, copy the template and set non-empty, local-only
values for `POSTGRES_PASSWORD`, `MINIO_ROOT_USER`, and
`MINIO_ROOT_PASSWORD` in `.env`. Do not commit that file.

### Commands

```powershell
# Initial local configuration
Copy-Item .env.example .env

# Start all development infrastructure services
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d

# Stop services while preserving their named data volumes
docker compose --env-file .env -f infrastructure/docker-compose.yml down

# Follow logs from every service (use a service name to narrow the output)
docker compose --env-file .env -f infrastructure/docker-compose.yml logs -f
```

To intentionally remove all local development data, run
`docker compose --env-file .env -f infrastructure/docker-compose.yml down -v`.
This is destructive.

### Service connections

| Service | Host connection | Internal Docker connection | Notes |
| --- | --- | --- | --- |
| PostgreSQL with PostGIS | `127.0.0.1:5432` by default | `postgres:5432` | Database `agrodata`, user `agrodata`, and the password set in `POSTGRES_PASSWORD`. PostGIS is enabled when a new volume is initialised. |
| Mosquitto MQTT | `127.0.0.1:1883` by default | `mosquitto:1883` | Anonymous access is enabled for local development only; add authenticated production configuration before deployment. |
| Redis | `127.0.0.1:6379` by default | `redis:6379` | Persistence is enabled with append-only files. |
| MinIO API | `http://127.0.0.1:9000` by default | `http://minio:9000` | Sign in with the local `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`. |
| MinIO Console | `http://127.0.0.1:9001` by default | `http://minio:9001` | Browser administration console for development. |

Ports and connection settings can be adjusted through the ignored `.env` file;
their defaults are shown in `.env.example`.

## Documentation

See [the project audit](docs/project-audit.md) for the initial repository audit,
known gaps, risks, and recommended implementation order.
