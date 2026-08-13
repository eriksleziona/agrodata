# AgroData Project Audit

**Audit date:** 2026-08-13  
**Scope:** Complete checked-out worktree and local Git metadata, inspected before making changes.

## Executive summary

The repository has been initialized but contains no committed or working-tree
project files. Its sole top-level entry was `.git`; it has no commits on the
`main` branch. Consequently, no current AgroData implementation, dependency
manifest, source module, schema, service definition, test suite, or deployment
configuration is present to audit.

The intended architecture below is derived from the project description supplied
for this audit, not from implementation files. It should be treated as a target
architecture.

## Current directory and repository structure

```text
agrodata/
└── .git/                   # Git repository metadata only
```

Observations:

- The worktree has no `backend`, `frontend`, `edge`, `firmware`, `simulator`,
  `gis`, `satellite`, `analytics`, `infrastructure`, `docs`, or `tests`
  directories yet (the `docs` directory is created by this audit document).
- There is no initial commit and no files tracked by Git.
- A remote named `origin` is configured, pointing to the AgroData GitHub
  repository. No remote content was fetched as part of this offline audit.

## Current architecture

No runtime architecture exists in the checked-out repository.

The stated target architecture is a modular platform with these concerns:

| Layer | Intended technology / responsibility | Current state |
| --- | --- | --- |
| Web frontend | React, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, MapLibre | Not implemented |
| API backend | Python, FastAPI, SQLAlchemy, Pydantic, Alembic | Not implemented |
| Primary data store | PostgreSQL with PostGIS | Not configured |
| Messaging / cache | MQTT (Mosquitto) and Redis | Not configured |
| Edge runtime | Python on Raspberry Pi; SQLite, GNSS/RTK, IMU, CAN, LTE integration | Not implemented |
| Object storage | S3-compatible storage / MinIO | Not configured |
| Delivery infrastructure | Docker, Docker Compose, Nginx | Not configured |
| Validation | Pytest, Vitest, Playwright | Not configured |

## Current dependencies

No dependency manifests exist. In particular, the repository does not contain
`pyproject.toml`, `requirements*.txt`, `poetry.lock`, `uv.lock`, `package.json`,
or a frontend lockfile. Therefore, no installed or declared application
dependencies can be identified.

## Current database structure and configuration

No database configuration or schema is present.

- No SQLAlchemy engine/session configuration, Pydantic settings, or environment
  template exists.
- No Alembic configuration or migration history exists.
- No PostgreSQL/PostGIS service configuration, database model, spatial column,
  index, or seed data exists.
- No UUID, timestamp, tenancy, authorization, retention, or backup policy is
  represented in code or infrastructure files.

## Current API structure

No FastAPI application or API modules are present.

- No route handlers, routers, dependency injection, schemas, services,
  repositories, authentication, authorization, error handling, or API versioning
  exist.
- No OpenAPI customisation, health/readiness endpoints, or request logging is
  configured.
- No API contract can be inferred, so compatibility analysis is not applicable.

## Current frontend structure

No frontend source or build configuration is present.

- No Vite project, React components, route structure, state/query clients,
  styling configuration, MapLibre integration, or environment configuration
  exists.
- No frontend API client, error/loading states, authentication flow, or map
  coordinate-handling conventions are defined.

## Current infrastructure

No infrastructure-as-code or local runtime configuration is present.

- No Dockerfiles, Compose file, Nginx configuration, `.env.example`, CI workflow,
  production deployment manifest, or observability configuration exists.
- MQTT, Redis, PostgreSQL/PostGIS, and MinIO are not provisioned.
- There is no documented local-development startup path, secret-management
  strategy, persistent-volume policy, database backup process, or service health
  check.

## Existing backend and frontend modules

There are no backend or frontend modules to inventory. The planned domain areas
listed in the project description—farm management, GIS, GNSS/RTK, telemetry,
IoT sensors, jobs, coverage, satellite data, weather, analytics, reporting, and
AI—have no current implementation in this worktree.

## Existing tests

No test directories, test configuration, fixtures, or test files exist.

- No Pytest suite is configured for backend services.
- No Vitest setup exists for frontend units/components.
- No Playwright configuration or end-to-end tests exist.
- No database integration, migration, API contract, GIS, edge-device, or
  container smoke tests exist.

## Missing components

Everything required for the proposed AgroData platform remains to be created.
The foundational missing components are:

1. Repository conventions: `.gitignore`, README, licence decision, contribution
   guidance, environment templates, formatting/linting/type-check settings, and
   CI.
2. Backend foundation: FastAPI app, configuration layer, database session,
   Alembic migrations, base models, UUID/UTC conventions, structured errors,
   health endpoints, and service/repository boundaries.
3. Identity and tenant model: organisations/farms, users, roles, authentication,
   authorisation, audit trail, and data-isolation rules.
4. Spatial foundation: PostGIS database service, coordinate reference system
   policy, field/boundary models, validation, spatial indexes, and GeoJSON API
   conventions.
5. Frontend foundation: Vite/React project, typed API client, routing, query and
   state setup, styling, authentication UI, and MapLibre baseline.
6. Local platform services: Compose configuration for PostGIS, Redis, Mosquitto,
   MinIO, backend, frontend, reverse proxy, volumes, and health checks.
7. Initial vertical feature: a farm/field workflow that proves authentication,
   tenancy, spatial storage, API contracts, map rendering, and tests end to end.
8. Edge and data ingestion: device registration, MQTT topic/versioning policy,
   telemetry validation and persistence, offline SQLite synchronisation, and
   device security.
9. Operations: secrets/configuration strategy, migrations on deployment,
   backups, logging, metrics, tracing, monitoring, and alerting.
10. Domain expansions: jobs and coverage, sensors, GNSS/RTK, satellite/weather
    integrations, analytics/reports, then AI capabilities.

## Potential architectural problems and technical debt

There is no code-level technical debt yet; however, the empty repository means
the following architectural decisions are currently unrecorded and pose delivery
risk if postponed:

| Risk | Consequence | Recommended early decision |
| --- | --- | --- |
| No tenancy/security model | Farm data could be exposed across organisations | Define organisations, memberships, roles, row-level access strategy, and audit requirements before domain APIs |
| No spatial policy | Inconsistent geometry, area, and distance calculations | Standardise API geometry as GeoJSON and store geographic data in a documented PostGIS SRID; define when to transform for measurements |
| No telemetry contract | Edge, MQTT, and backend implementations may drift | Version device registration, MQTT topics, payload schemas, retry/ordering rules, and idempotency keys before firmware work |
| No data lifecycle policy | High-volume telemetry and imagery can become costly and slow | Define retention, partitioning, object-storage ownership, aggregation, and deletion policies early |
| No API boundaries | Frontend and backend can become tightly coupled | Introduce versioned routers and typed request/response schemas; keep business logic in services and persistence in repositories |
| No deployment baseline | Local, test, and production environments may diverge | Compose the full local stack, use environment variables, and add health checks plus migrations from the outset |
| No test/CI baseline | Regressions and schema drift will accumulate | Add automated linting, type checking, unit/integration tests, migrations tests, and browser smoke tests with the first feature |
| Broad domain scope | Parallel features can create incompatible abstractions | Deliver narrow vertical slices and defer AI until clean, governed operational data exists |

## Recommended implementation order

1. Establish repository baseline: README, directory skeleton, Git ignore rules,
   environment templates without secrets, code-quality configuration, and CI.
2. Define the core data and security design: users, organisations, farms,
   membership/roles, UUIDs, UTC timestamps, audit requirements, and spatial CRS
   policy.
3. Build the backend foundation: FastAPI app factory, settings, error model,
   SQLAlchemy/Alembic setup, PostGIS enablement, health endpoints, and Pytest
   database fixtures.
4. Create the local infrastructure baseline with Docker Compose: PostGIS, Redis,
   Mosquitto, MinIO, backend, frontend, Nginx, named volumes, and health checks.
5. Build the frontend foundation: Vite/React/TypeScript, Tailwind, routing,
   typed API client, TanStack Query, Zustand boundaries, and Vitest/Playwright
   setup.
6. Deliver an authenticated farm-and-field vertical slice: field CRUD with
   GeoJSON boundaries, PostGIS validation/indexing, MapLibre rendering, API
   integration, and backend/frontend/end-to-end tests.
7. Add agricultural jobs and coverage, reusing the tenancy and spatial
   foundations.
8. Introduce device identity and telemetry ingestion: secured MQTT, versioned
   messages, idempotent persistence, Redis only where justified, and edge sync
   contracts.
9. Add sensor, GNSS/RTK, and machine telemetry workflows, including volume and
   retention controls.
10. Integrate weather, satellite imagery, object storage, analytics, and reports
    once the foundational data contracts are stable.
11. Add AI capabilities last, with explicit data quality, governance, evaluation,
    and human-review requirements.

## Audit limitations

This is an inventory of the local checkout only. The configured Git remote was
not accessed, dependencies were not installed, and no services were started.
If project sources exist on another branch, remote, disk location, or archive,
they must be made available in this worktree before a code-level audit can be
performed.
