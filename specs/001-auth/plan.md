# specs/001-auth/plan.md

## Overview
Building user authentication and role-based access control as a standalone library with CLI interface. Core auth logic (JWT, bcrypt, user management) will be in importable modules with FastAPI routes as a thin veneer. The library exposes CLI commands for user management with JSON output.

## Constitutional Gate Review

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | ✓ | AuthService and UserService are standalone classes, routes are thin wrappers |
| CLI Mandate | ✓ | Auth library exposes CLI for user management (create, list, update roles) with JSON stdout |
| Test-First | ✓ | Each service method has contract tests before implementation |
| Integration-First | ✓ | Real PostgreSQL, real bcrypt, real JWT - no mocks except for rate limiting Redis |
| Simplicity Gate | ✓ | 1 entity (User), 4 endpoints (register, login, refresh, me) + 3 admin endpoints |
| Single Domain Model | ✓ | Single User model, no DTOs - Pydantic schemas only for API serialization boundary |

## Dependencies

### Cross-Feature (from master-spec.md)
| Feature | What We Import | Status |
|---------|----------------|--------|
| 001A-infrastructure | TimestampMixin, success_response, list_response, get_db | Required |

### External Libraries
| Library | Version | Purpose |
|---------|---------|--------|
| python-jose | >=3.3.0 | JWT encoding/decoding |
| passlib | >=1.7.4 | bcrypt password hashing |
| slowapi | >=0.1.9 | Rate limiting |
| redis | >=5.0.0 | Rate limit storage |

## Implementation Phases

### Phase 1: Contracts & Interfaces
- [ ] User model with SQLAlchemy (users table, UserRole enum)
- [ ] AuthService interface (register, authenticate, create_tokens, verify_token)
- [ ] UserService interface (list, update_role, delete)
- [ ] Pydantic schemas (UserCreate, UserResponse, LoginRequest, TokenResponse)
Estimate: ~150 LOC

### Phase 2: Test Infrastructure  
- [ ] Test database setup with async session
- [ ] User factory for test data generation
- [ ] JWT test utilities (create valid/expired tokens)
- [ ] Rate limiting test mocks (Redis)
Estimate: ~200 LOC

### Phase 3: Data Layer
- [ ] User SQLAlchemy model implementation
- [ ] Alembic migration for users table
- [ ] Database indexes (email unique, role)
- [ ] Seed data for development (admin, gm, viewer users)
Estimate: ~100 LOC

### Phase 4: Core Logic
- [ ] AuthService implementation (bcrypt, JWT, account locking)
- [ ] UserService implementation (CRUD operations)
- [ ] Password validation and security utilities
- [ ] Rate limiting service with Redis backend
Estimate: ~300 LOC

### Phase 5: API Layer
- [ ] Auth routes (register, login, refresh, me)
- [ ] User management routes (list, update, delete - admin only)
- [ ] Auth dependencies (get_current_user, require_role)
- [ ] Rate limiting middleware integration
Estimate: ~250 LOC

### Phase 6: CLI
- [ ] CLI module with typer for user management
- [ ] Commands: create-user, list-users, update-role, delete-user
- [ ] JSON output format, errors to stderr
- [ ] Integration with existing services
Estimate: ~150 LOC

## Parallel Work Opportunities
- Phase 1 & 2 can run concurrently (contracts + test setup)
- Phase 4 core logic can start once Phase 1 contracts are complete
- CLI (Phase 6) can be developed alongside API layer (Phase 5)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JWT secret key management | Low | High | Clear env var documentation, validation on startup |
| Rate limiting Redis dependency | Medium | Medium | Graceful degradation if Redis unavailable |
| Password policy complexity | Low | Low | Simple 8-char minimum per NIST guidelines |
| Cross-role data access | Medium | High | Comprehensive authorization tests for each role |

## Total Estimate
~1150 LOC across 24 tasks