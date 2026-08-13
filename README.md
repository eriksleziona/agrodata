# AgroData

AgroData is a planned precision-agriculture platform for farm management, GIS,
GNSS/RTK, machine telemetry, IoT sensors, jobs, field coverage, satellite
imagery, weather, analytics, reporting, and future AI-assisted workflows.

## Project status

This repository currently contains the initial project foundation only. It has
no business logic, API routes, database models, migrations, or runnable services
yet.

## Target architecture

\`\`\`text
React + TypeScript frontend
            |
         FastAPI
            |
PostgreSQL/PostGIS  Redis  MQTT  S3-compatible storage
            |
  Edge devices, GNSS/RTK, sensors, and machine telemetry
\`\`\`

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
| \`backend/\` | API, application services, repositories, and migrations. |
| \`frontend/\` | Web application and map-based user interface. |
| \`edge/\` | Edge-agent integration with GNSS, sensors, CAN, and offline storage. |
| \`firmware/\` | Firmware for supported field devices. |
| \`simulator/\` | Simulated devices and agricultural data sources. |
| \`gis/\` | Spatial-data conventions, processing, and reference material. |
| \`satellite/\` | Satellite imagery integrations and processing. |
| \`analytics/\` | Analytics pipelines, reporting, and future AI work. |
| \`infrastructure/\` | Container, proxy, and deployment configuration. |
| \`docs/\` | Architecture and operational documentation. |
| \`tests/\` | Cross-module integration and end-to-end tests. |

## Development workflow

1. Copy \`.env.example\` to a local \`.env\` file and enter values only on your
   machine. Keep credentials out of source control.
2. Make schema changes through Alembic migrations once the backend foundation is
   introduced; never edit deployed databases manually.
3. Put business rules in backend services, persistence access in repositories,
   and keep API route handlers thin.
4. Use UUID identifiers and UTC timestamps. Expose timestamps as ISO 8601 in
   APIs and use PostGIS for spatial data.
5. Add documentation and automated tests alongside every new feature.

## Local development commands

The scaffold contains no runnable service configuration yet. The following
commands prepare and verify the local workspace:

\`\`\`powershell
Copy-Item .env.example .env
Get-ChildItem -Directory
git status --short
\`\`\`

Once Docker Compose and the applications are added under \`infrastructure/\`, the
standard local startup command will be documented there. Do not run commands
that require credentials until their local \`.env\` values have been configured.

## Documentation

See [the project audit](docs/project-audit.md) for the initial repository audit,
known gaps, risks, and recommended implementation order.
