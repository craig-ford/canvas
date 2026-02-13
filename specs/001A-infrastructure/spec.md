# 001A-infrastructure — Infrastructure Spec

## Overview

Bootstrap infrastructure for the Canvas application: Docker Compose configuration (dev + prod profiles), Dockerfiles for backend and frontend, environment files, database setup, Alembic migration scaffolding, and shared backend utilities (config, db, response helpers, health endpoint).

## Functional Requirements

- FR-INFRA-001: Docker Compose with `dev` and `prod` profiles, service dependency ordering, health checks
- FR-INFRA-002: Backend Dockerfile with multi-stage build (dev + prod targets)
- FR-INFRA-003: Frontend Dockerfile with multi-stage build (dev + prod targets), Nginx config for prod
- FR-INFRA-004: `.env.dev` and `.env.prod` with all environment variables from cross-cutting.md
- FR-INFRA-005: PostgreSQL service with named volume, health check via `pg_isready`
- FR-INFRA-006: Backend `config.py` — Pydantic Settings loading all env vars
- FR-INFRA-007: Backend `db.py` — async SQLAlchemy engine + session factory
- FR-INFRA-008: Backend `main.py` — FastAPI app factory with CORS, exception handlers, router mounting, request ID middleware
- FR-INFRA-009: Alembic configuration with async support
- FR-INFRA-010: `GET /api/health` endpoint returning `{"status": "ok"}`
- FR-INFRA-011: Backend response helpers (`success_response`, `list_response`, error envelope)
- FR-INFRA-012: Frontend project scaffolding — Vite + React + TypeScript + Tailwind setup
- FR-INFRA-013: Frontend API client (Axios instance with auth interceptors)
- FR-INFRA-014: Frontend AppShell component (top bar, breadcrumbs, user menu)
- FR-INFRA-015: Seed data script (`python -m canvas.seed`) — idempotent, creates dev users + sample data

## Docker Compose Services

| Service | Image | Dev Port | Prod Port | Health Check | Depends On |
|---------|-------|----------|-----------|-------------|------------|
| db | postgres:18 | 5432:5432 | —:5432 | pg_isready -U canvas | — |
| backend | ./backend | 8000:8000 | 8000:8000 | GET /api/health | db (healthy) |
| frontend | ./frontend | 5173:5173 | 80:80 | curl localhost (prod) | backend (healthy) |

## Port Assignments

| Service | External (Dev) | External (Prod) | Internal |
|---------|---------------|-----------------|----------|
| Frontend (Vite) | 5173 | — | 5173 |
| Frontend (Nginx) | — | 80 | 80 |
| Backend | 8000 | 8000 | 8000 |
| PostgreSQL | 5432 | — | 5432 |

## Environment Variables

See `specs/cross-cutting.md` — all variables owned by 001A-infrastructure:
- CANVAS_DATABASE_URL
- CANVAS_CORS_ORIGINS
- CANVAS_LOG_LEVEL
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

## Security Requirements

- SEC-INFRA-001: `.env.dev` and `.env.prod` must NOT be committed to git (add to .gitignore)
- SEC-INFRA-002: CANVAS_SECRET_KEY must use a strong random value in production (not the dev default)
- SEC-INFRA-003: CORS origins restricted to known frontend URLs (no wildcard in prod)
- SEC-INFRA-004: PostgreSQL credentials use non-default values in production
- SEC-INFRA-005: Docker containers run as non-root user in production Dockerfiles
- SEC-INFRA-006: Health endpoint does NOT expose version, dependency status, or internal details
- SEC-INFRA-007: Structured logging must NOT log request bodies containing passwords or tokens
- SEC-INFRA-008: Request ID middleware adds `X-Request-ID` header for traceability

## Testing Strategy

### Infrastructure Tests
- `test_health_endpoint()`: GET /api/health returns 200 with `{"status": "ok"}`
- `test_cors_headers()`: OPTIONS request returns correct CORS headers
- `test_request_id_header()`: Response includes X-Request-ID header
- `test_error_envelope()`: Invalid routes return standard error envelope format
- `test_db_connection()`: AsyncSession can execute a simple query
- `test_seed_idempotent()`: Running seed script twice produces no errors or duplicates

### Docker Tests (manual verification)
- Dev profile starts all 3 services with health checks passing
- Prod profile builds and serves frontend via Nginx, proxies /api to backend
- Database volume persists data across container restarts

## Acceptance Criteria

- AC-INFRA-01: `docker compose --profile dev up` starts all 3 services, backend passes health check
- AC-INFRA-02: `docker compose --profile prod up` builds and starts all 3 services, Nginx serves frontend and proxies /api
- AC-INFRA-03: Backend connects to PostgreSQL, Alembic migrations run on boot
- AC-INFRA-04: `GET /api/health` returns 200 with `{"status": "ok"}`
- AC-INFRA-05: Frontend loads in browser at dev port, shows AppShell
- AC-INFRA-06: Seed script creates dev users and sample data without errors
- AC-INFRA-07: Request ID appears in response headers and structured logs
