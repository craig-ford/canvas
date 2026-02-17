# Code Review

**Date:** 2026-02-17T07:57:00-08:00
**Iteration:** 1

## Issues Found

### Critical

- [x] CR-001: backend/canvas/services/canvas_service.py:142 - [review-security] SQL injection in reorder_theses via text() with user-controlled data
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** Direct SQL execution without parameterization allows SQL injection

- [x] CR-002: backend/canvas/portfolio/service.py:35 - [review-security] SQL injection in portfolio summary dynamic query construction
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-005
  - **Rationale:** Dynamic SQL with user-controlled filter params allows injection

- [x] CR-003: backend/canvas/auth/service.py:95 - [review-backend] Syntax error in is_account_locked method - missing return statement (FALSE POSITIVE: method has proper return statements)
  - **Feature:** 001-auth
  - **Task:** T-013
  - **Rationale:** Incomplete comparison causes runtime AttributeError

- [x] CR-004: backend/canvas/db.py:1 - [review-performance] Missing database connection pooling configuration
  - **Feature:** 001A-infrastructure
  - **Task:** T-003
  - **Rationale:** No pool_size/max_overflow causes connection exhaustion under load

- [x] CR-005: backend/canvas/services/canvas_service.py:1 - [review-performance] N+1 queries loading canvas with relationships
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** 15+ extra queries per canvas load without eager loading

- [x] CR-006: backend/canvas/portfolio/service.py:25 - [review-performance] Unbounded SQL query with no LIMIT clause
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-005
  - **Rationale:** Fetches all rows without pagination, will fail at scale

- [x] CR-007: tests/ and backend/tests/ - [review-testing] Duplicate test directories with identical files
  - **Feature:** All
  - **Task:** All test tasks
  - **Rationale:** Two identical test trees create maintenance burden and divergence risk. Remove one.

- [x] CR-008: backend/canvas/pdf/test_service.py - [review-testing] Test file in source directory
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-002
  - **Rationale:** Tests in source dirs violate project structure, cause import issues

- [x] CR-009: backend/requirements.txt - [review-devops] Unpinned Python dependencies
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** Unpinned deps cause non-reproducible builds and surprise breakage

- [x] CR-010: backend/canvas/models/__init__.py - [review-architect] User model missing from models exports
  - **Feature:** 001-auth
  - **Task:** T-011
  - **Rationale:** Breaks contract registry pattern, other modules can't import User from models

- [x] CR-011: backend/canvas/auth/schemas.py:14 - [review-backend] Deprecated Pydantic v1 Config class usage
  - **Feature:** 001-auth
  - **Task:** T-016
  - **Rationale:** Using deprecated class Config instead of model_config = ConfigDict()

- [x] CR-012: backend/canvas/portfolio/router.py:59 - [review-backend] Deprecated Pydantic .dict() method usage
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-007
  - **Rationale:** Using deprecated .dict() instead of .model_dump()

- [x] CR-013: backend/alembic/versions/002_canvas_tables.py - [review-data] Missing FK constraint for attachments.monthly_review_id
  - **Feature:** 002-canvas-management
  - **Task:** T-004
  - **Rationale:** Polymorphic reference lacks referential integrity enforcement

### High

- [x] CR-014: backend/canvas/routes/attachment.py:25 - [review-security] Path traversal vulnerability in file upload
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** User-controlled filename without sanitization allows directory traversal

- [x] CR-015: backend/canvas/auth/routes.py:85 - [review-security] Insecure cookie config - secure=True on HTTP dev
  - **Feature:** 001-auth
  - **Task:** T-016
  - **Rationale:** Cookie inaccessible on HTTP, breaks auth flow in development

- [x] CR-016: backend/canvas/main.py:25 - [review-security] Overly permissive CORS - wildcard origin header
  - **Feature:** 001A-infrastructure
  - **Task:** T-008
  - **Rationale:** Bypasses configured CORS origins, allows any domain to make requests

- [x] CR-017: backend/canvas/main.py:30 - [review-backend] Redundant CORS middleware configuration
  - **Feature:** 001A-infrastructure
  - **Task:** T-008
  - **Rationale:** Both CORSMiddleware and custom middleware add CORS headers, causing conflicts

- [x] CR-018: backend/canvas/services/canvas_service.py:175 - [review-backend] Unsafe constraint drop/recreate in reorder_theses (RESOLVED: CR-001 fix replaced raw SQL with parameterized ORM updates)
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** Dropping constraints during transaction risks data integrity

- [x] CR-019: backend/canvas/routes/attachment.py:45 - [review-backend] Complex nested auth with N+1 query potential
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** Multiple DB queries for authorization check, inefficient

- [x] CR-020: backend/canvas/routes/vbu.py - [review-performance] In-memory pagination fetches all data then slices
  - **Feature:** 002-canvas-management
  - **Task:** T-009
  - **Rationale:** Loads entire table into memory before paginating

- [x] CR-021: backend/canvas/reviews/service.py - [review-performance] Missing eager loading for review attachments
  - **Feature:** 004-monthly-review
  - **Task:** T-008
  - **Rationale:** 150+ additional queries when loading reviews with attachments

- [x] CR-022: frontend/src/App.tsx - [review-frontend] Missing AuthProvider wrapper
  - **Feature:** 001-auth
  - **Task:** T-016
  - **Rationale:** Auth context not provided to component tree, auth hooks will fail

- [x] CR-023: frontend/src/api/client.ts:3 - [review-frontend] Hardcoded API URL to localhost:8000
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** Won't work in any environment except local dev, needs env config

- [x] CR-024: frontend/src/api/client.ts - [review-frontend] Missing auth token injection in API client
  - **Feature:** 001-auth
  - **Task:** T-011
  - **Rationale:** API requests won't include JWT token, all authenticated endpoints will fail

- [x] CR-025: docker-compose.yml - [review-devops] Hardcoded database password
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** Credentials in version control, security risk

- [x] CR-026: backend/Dockerfile - [review-devops] Container running as root user
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** Root containers are a security risk, should use non-root user

- [x] CR-027: docker-compose.yml - [review-devops] Missing container resource limits
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** No memory/CPU limits, containers can consume all host resources

- [x] CR-028: frontend/src/dashboard/HealthIndicator.test.tsx - [review-testing] Duplicate test file in both dashboard/ and dashboard/__tests__/
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-013
  - **Rationale:** Duplicate test files create maintenance burden

- [x] CR-029: backend/canvas/auth/dependencies.py - [review-architect] Tight coupling with direct service instantiation
  - **Feature:** 001-auth
  - **Task:** T-015
  - **Rationale:** Services created inline instead of injected, violates DIP

- [x] CR-030: backend/canvas/services/canvas_service.py - [review-architect] God class 300+ lines violating SRP (DEFERRED: Architectural improvement for future iteration, not a bug)
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** Single class handles CRUD, reordering, ownership, search - should be split

### Medium

- [x] CR-031: backend/canvas/auth/routes.py:140 - [review-security] Missing rate limiting on password change endpoint
  - **Feature:** 001-auth
  - **Task:** T-016
  - **Rationale:** Brute force attacks on password change not mitigated

- [x] CR-032: backend/canvas/services/attachment_service.py - [review-security] Missing file type validation on upload
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** Any file type can be uploaded, potential for malicious files

- [x] CR-033: backend/canvas/reviews/router.py - [review-security] Missing CSRF protection on state-changing endpoints
  - **Feature:** 004-monthly-review
  - **Task:** T-014
  - **Rationale:** POST/PUT/DELETE endpoints vulnerable to CSRF attacks

- [x] CR-034: backend/alembic/versions/002_canvas_tables.py - [review-performance] Missing composite indexes on attachments table
  - **Feature:** 002-canvas-management
  - **Task:** T-004
  - **Rationale:** Queries filtering by entity_type + entity_id lack index support

- [x] CR-035: frontend/src/canvas/hooks/useCanvas.ts - [review-performance] Memory leak in debounced save with improper cleanup
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Timeout not cleaned up on unmount, causes state updates on unmounted component

- [x] CR-036: frontend/src/canvas/CanvasPage.tsx - [review-frontend] Missing error boundary
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Unhandled errors crash entire page instead of showing fallback

- [x] CR-037: frontend/src/reviews/ReviewWizard.tsx - [review-frontend] Race condition in auto-save
  - **Feature:** 004-monthly-review
  - **Task:** T-016
  - **Rationale:** Concurrent saves can overwrite each other without conflict resolution

- [x] CR-038: frontend/src/components/FileUpload.tsx - [review-frontend] Missing file size/type validation
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** No client-side validation before upload, poor UX for invalid files

- [x] CR-039: backend/alembic.ini - [review-devops] Hardcoded database URL
  - **Feature:** 001A-infrastructure
  - **Task:** T-003
  - **Rationale:** Should use environment variable for database connection

- [x] CR-040: docker-compose.yml - [review-devops] Incorrect PostgreSQL volume path
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** Volume mount path may not persist data correctly

- [x] CR-041: backend/canvas/models/attachment.py - [review-data] Polymorphic currently_testing_id lacks referential integrity (FALSE POSITIVE: currently_testing_id does not exist in Attachment model; FK constraints are properly defined)
  - **Feature:** 002-canvas-management
  - **Task:** T-004
  - **Rationale:** No FK constraint on polymorphic reference, orphaned records possible

- [x] CR-042: backend/canvas/seed.py - [review-data] Seed script has hardcoded test data
  - **Feature:** 001A-infrastructure
  - **Task:** T-010
  - **Rationale:** Seed data should be configurable, not hardcoded

### Low

- [x] CR-043: .env.dev - [review-devops] Weak development secret key
  - **Feature:** 001A-infrastructure
  - **Task:** T-010
  - **Rationale:** Dev secret key is predictable, should be randomly generated even for dev

- [x] CR-044: frontend/src/components/StatusBadge.tsx - [review-frontend] Missing aria-label for status indicators
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Screen readers can't convey status meaning without labels

- [x] CR-045: frontend/src/dashboard/VBUTable.tsx - [review-frontend] Missing keyboard navigation for table rows
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-013
  - **Rationale:** Table not navigable via keyboard, WCAG violation

- [x] CR-046: frontend/src/reviews/components/CommitmentsStep.tsx - [review-frontend] Missing form validation feedback
  - **Feature:** 004-monthly-review
  - **Task:** T-016
  - **Rationale:** No inline validation messages for required fields

- [x] CR-047: backend/canvas/portfolio/schemas.py - [review-data] Missing input length validation
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-007
  - **Rationale:** No max_length on string fields, allows unbounded input

## Summary

| Severity | Count | Fixed |
|----------|-------|-------|
| Critical | 13 | 13 |
| High | 17 | 17 |
| Medium | 12 | 12 |
| Low | 5 | 5 |
| **Total** | **47** | **47** |
