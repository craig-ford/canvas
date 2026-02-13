# specs/001A-infrastructure/plan.md

## Overview

Bootstrap infrastructure for Canvas application: Docker Compose with dev/prod profiles, Dockerfiles, environment configuration, PostgreSQL setup, Alembic scaffolding, FastAPI app factory with middleware, shared utilities, and frontend scaffolding with Vite + React + Tailwind.

## Constitutional Gate Review

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | ✓ | Backend utilities (config, db, response helpers) are importable modules. Frontend API client is reusable. |
| CLI Mandate | ✓ | Seed script exposes CLI: `python -m canvas.seed` with JSON stdout for success/error reporting. |
| Test-First | ✓ | Health endpoint, CORS, response helpers, DB connection all have clear contracts for testing first. |
| Integration-First | ✓ | Real PostgreSQL in Docker, real HTTP requests via httpx, no mocks for infrastructure. |
| Simplicity Gate | ✓ | 3 core entities (Docker services), 1 health endpoint, minimal middleware. No premature abstraction. |
| Single Domain Model | ✓ | TimestampMixin shared across all models, single response envelope pattern. |

## Dependencies

### Cross-Feature (from master-spec.md)
| Feature | What We Import | Status |
|---------|----------------|--------|
| None | This is the foundation feature | N/A |

### External Libraries
| Library | Version | Purpose |
|---------|---------|--------|
| FastAPI | >=0.128.0 | Async web framework |
| SQLAlchemy | >=2.0 | Async ORM |
| asyncpg | Latest | PostgreSQL async driver |
| Alembic | >=1.14 | Database migrations |
| Pydantic | >=2.13.0 | Settings and validation |
| structlog | Latest | JSON structured logging |
| pytest | Latest | Testing framework |
| httpx | Latest | Async HTTP client for tests |
| React | >=19.2.0 | Frontend framework |
| Vite | >=6.0 | Build tool |
| Tailwind CSS | >=4.0 | CSS framework |
| Axios | >=1.7 | HTTP client |

## Implementation Phases

### Phase 1: Contracts & Interfaces
- [ ] TimestampMixin base class with UUID primary key
- [ ] Response envelope interfaces (success_response, list_response, error_envelope)
- [ ] Config class interface with all environment variables
- [ ] Database session factory interface
- [ ] Health endpoint contract
Estimate: ~50 LOC

### Phase 2: Test Infrastructure
- [ ] pytest configuration with async support
- [ ] Test database setup with Docker
- [ ] Health endpoint test
- [ ] CORS headers test
- [ ] Response envelope format tests
- [ ] Database connection test
Estimate: ~100 LOC

### Phase 3: Data Layer
- [ ] PostgreSQL Docker service with health check
- [ ] Alembic configuration with async support
- [ ] Database engine and session factory
- [ ] TimestampMixin implementation
- [ ] Initial migration (empty, for testing)
Estimate: ~80 LOC

### Phase 4: Core Logic
- [ ] Pydantic Settings class loading all env vars
- [ ] Response helper functions
- [ ] Request ID middleware
- [ ] Exception handlers with error envelope
- [ ] Seed script with CLI interface
Estimate: ~120 LOC

### Phase 5: API Layer
- [ ] FastAPI app factory
- [ ] CORS middleware configuration
- [ ] Health endpoint implementation
- [ ] Router mounting structure
- [ ] Structured logging setup
Estimate: ~80 LOC

### Phase 6: UI
- [ ] Vite + React + TypeScript project setup
- [ ] Tailwind CSS configuration
- [ ] Axios client with interceptors
- [ ] AppShell component (header, navigation)
- [ ] Docker setup for frontend (dev + prod)
Estimate: ~150 LOC

## Parallel Work Opportunities
- Phase 3 (Database) and Phase 6 (Frontend setup) can run concurrently
- Docker Compose services can be developed in parallel
- Frontend and backend Dockerfiles can be created simultaneously

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Docker Compose networking issues | Medium | High | Use explicit service names, test health checks |
| Alembic async configuration complexity | Medium | Medium | Follow SQLAlchemy 2.0 async patterns, test with real DB |
| Frontend build optimization | Low | Medium | Use Vite defaults, multi-stage Docker builds |
| Environment variable conflicts | Low | High | Clear naming convention, validation in Settings class |

## Total Estimate
~580 LOC across 12 tasks