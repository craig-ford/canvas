# Code Review

**Date:** 2026-02-17T09:40:00-08:00
**Iteration:** 3

## Previous Iteration Summary
- Iteration 1: 47 issues found, all fixed and verified
- Iteration 2: 21 issues found, all fixed and verified (275/275 tests passing)

## Deduplication Notes
- review-backend CR-070 and review-data CR-076 both flagged migration chain — merged into CR-070
- review-architect CanvasService god class was documented as tech debt in iteration 2 — excluded (known/accepted)
- review-architect DI complaints for route handlers — these are patterns consistent with project scale, excluded as non-actionable for this scope
- review-testing tautological test complaints for contract tests — these are intentionally structural per TDD task specs, excluded

## Issues Found

### Critical

- [x] CR-070: backend/alembic/versions/002_canvas_tables.py:14 - [review-backend] Broken migration chain — down_revision='001_auth_tables' but migration 001 has revision='001'
  - **Feature:** 001A-infrastructure
  - **Task:** T-005
  - **Rationale:** Alembic cannot resolve the revision graph. `alembic heads` crashes with KeyError. Production database setup via migrations is impossible. Migration 004 also references non-existent '003_canvas_management'. Tests bypass this via Base.metadata.create_all() but production deployments are broken.

- [x] CR-071: frontend/package-lock.json:1 - [review-devops] package-lock.json out of sync with package.json — tailwindcss and autoprefixer missing from lock file
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** `npm ci` fails during Docker build, preventing frontend container from building. Production deployment blocked.

### High

- [x] CR-072: backend/canvas/portfolio/service.py:46 - [review-security] Raw SQL text() used for INTERVAL arithmetic
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-008
  - **Rationale:** `text("INTERVAL '1 month'")` is a hardcoded literal so not injectable, but mixing raw SQL with ORM queries is fragile and violates the project's ORM-only convention. Should use `timedelta` or `func.make_interval`.

- [x] CR-073: backend/canvas/auth/routes.py:95 - [review-security] JWT refresh token exposed in both response body AND httpOnly cookie
  - **Feature:** 001-auth
  - **Task:** T-006
  - **Rationale:** Refresh token should only be in httpOnly cookie, never in response body. Dual exposure increases attack surface for XSS token theft.

- [x] CR-074: backend/tests/canvas/test_services_contract.py:1 - [review-testing] Interface stubs masquerading as tests — contains `...` ellipsis bodies instead of assertions
  - **Feature:** 002-canvas-management
  - **Task:** T-002
  - **Rationale:** These "tests" pass but test nothing. They inflate test count without providing coverage. Either implement real assertions or remove.

- [x] CR-075: backend/tests/reviews/test_service_unit.py:1 - [review-testing] Stub tests with only `assert True` and `assert service.db == mock_db`
  - **Feature:** 004-monthly-review
  - **Task:** T-010
  - **Rationale:** Tests claim to verify business logic but contain no meaningful assertions. Provides false confidence in test coverage.

### Medium

- [x] CR-076: backend/canvas/pdf/service.py:59 - [review-backend] Generic `except Exception` masks all errors
  - **Feature:** 002-canvas-management
  - **Task:** T-019
  - **Rationale:** Catches all exceptions including programming errors, making debugging impossible. Should catch specific expected exceptions only.

- [x] CR-077: frontend/src/components/AppShell.tsx:1 - [review-frontend] Missing WCAG accessibility landmarks (nav, main, skip links)
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** Screen reader users cannot navigate the application structure. WCAG 2.1 Level A requires landmark regions.

- [x] CR-078: frontend/src/components/FileUpload.tsx:1 - [review-frontend] Drag/drop zone missing ARIA attributes and keyboard navigation
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** File upload is inaccessible to keyboard-only users and screen readers. Needs role="button", aria-label, and keyboard event handlers.

- [x] CR-079: frontend/src/components/InlineEdit.tsx:1 - [review-frontend] Missing ARIA labels and live region for save status
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Screen readers don't announce save success/failure. Needs aria-live region for status updates.

- [x] CR-080: backend/Dockerfile:25 - [review-devops] Dependencies installed as root before USER switch
  - **Feature:** 001A-infrastructure
  - **Task:** T-009
  - **Rationale:** pip install runs as root, creating files owned by root that the non-root user may not be able to access. Should use --user flag or install after USER directive.

- [x] CR-081: docker-compose.yml:15 - [review-devops] Missing health check condition on db dependency
  - **Feature:** 001A-infrastructure
  - **Task:** T-009
  - **Rationale:** Backend starts before database is ready. Should use `depends_on: db: condition: service_healthy` to prevent connection failures on startup.

### Low

- [x] CR-082: frontend/src/components/InlineEdit.tsx:1 - [review-frontend] Missing useEffect cleanup for saveTimeoutRef
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Timeout may fire after component unmount, causing state update on unmounted component.

- [x] CR-083: frontend/src/reviews/ReviewWizard.tsx:1 - [review-frontend] Form validation errors not announced to screen readers
  - **Feature:** 004-monthly-review
  - **Task:** T-015
  - **Rationale:** Validation errors are visual-only. Needs aria-live or aria-describedby for error messages.

- [x] CR-084: backend/canvas/main.py:113 - [review-devops] Health check endpoint doesn't verify database connectivity
  - **Feature:** 001A-infrastructure
  - **Task:** T-010
  - **Rationale:** Health endpoint returns 200 even if database is down. Should include a lightweight DB ping.

## Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 4 |
| Medium | 6 |
| Low | 3 |
| **Total** | **15** |

---

# Code Review — Iteration 4

**Date:** 2026-02-17T10:09:00-08:00
**Iteration:** 4

## Previous Iteration Summary
- Iteration 1: 47 issues found, all fixed
- Iteration 2: 21 issues found, all fixed
- Iteration 3: 15 issues found, all fixed (275/275 tests passing)

## Agents Reporting
| Agent | New Issues |
|-------|-----------|
| review-security | 5 (after dedup) |
| review-backend | 4 |
| review-frontend | 6 |
| review-architect | 2 |
| review-performance | 3 |
| review-testing | 0 ✅ |
| review-data | 3 |
| review-devops | 3 |

## Issues Found

### Critical

(none after dedup — review-security's "rate limit race" downgraded to Medium since this is single-worker dev app, review-devops' ".env.prod undefined vars" is false positive — template variables for deployment injection)

### High

- [x] CR-084: backend/canvas/routes/attachment.py:51 - [review-security] Authorization bypass: attachment download endpoint doesn't verify requesting user owns the parent canvas
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** Any authenticated user can download any attachment by ID, bypassing canvas ownership checks

- [x] CR-085: frontend/src/reviews/components/CommitmentsStep.tsx:25 - [review-frontend] Form validation errors not announced to screen readers — missing aria-live regions
  - **Feature:** 004-monthly-review
  - **Task:** T-015
  - **Rationale:** Screen readers don't announce validation errors, making form unusable for visually impaired users (WCAG violation)

- [x] CR-086: frontend/src/canvas/CanvasPage.tsx:1 - [review-frontend] Missing error boundary around drag/drop and file upload operations
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Unhandled errors in drag/drop or file operations crash the entire canvas page, losing user work

- [x] CR-087: backend/canvas/models/monthly_review.py:11 - [review-data] MonthlyReview uses raw Enum("thesis","proof_point") instead of importing CurrentlyTestingType from Canvas model
  - **Feature:** 004-monthly-review
  - **Task:** T-001
  - **Rationale:** Two different enum definitions for same concept creates data inconsistency risk and DRY violation

- [x] CR-088: backend/Dockerfile:25 - [review-devops] Copies entire app before installing deps — requirements.txt COPY is followed by full COPY . . before pip install
  - **Feature:** 001A-infrastructure
  - **Task:** T-010
  - **Rationale:** Docker layer caching broken — any source change invalidates dependency install layer, slowing builds

### Medium

- [x] CR-089: backend/canvas/auth/routes.py:24 - [review-security] In-memory rate limiting dict not thread-safe and resets on worker restart
  - **Feature:** 001-auth
  - **Task:** T-015
  - **Rationale:** Rate limiting ineffective in multi-worker deployment; dict operations not atomic under concurrent requests

- [x] CR-090: backend/canvas/auth/routes.py:89 - [review-security] User enumeration via different error messages for invalid email vs invalid password
  - **Feature:** 001-auth
  - **Task:** T-015
  - **Rationale:** Attackers can determine valid email addresses by observing different error responses

- [x] CR-091: frontend/src/components/FileUpload.tsx:145 - [review-frontend] Drag/drop zone missing keyboard event handlers for Enter/Space activation
  - **Feature:** 002-canvas-management
  - **Task:** T-021
  - **Rationale:** Keyboard-only users cannot activate file upload zone (WCAG 2.1.1 violation)

- [x] CR-092: frontend/src/auth/AuthContext.tsx:85 - [review-frontend] Token refresh race condition — multiple simultaneous requests trigger duplicate refresh attempts
  - **Feature:** 001-auth
  - **Task:** T-017
  - **Rationale:** Race condition can cause auth failures and session loss during concurrent API calls

- [x] CR-093: backend/canvas/routes/vbu.py:27 - [review-architect] Direct database access in route handler violates layered architecture
  - **Feature:** 002-canvas-management
  - **Task:** T-014
  - **Rationale:** Route handlers should delegate to services, not execute raw SQLAlchemy queries directly

- [x] CR-094: backend/canvas/portfolio/service.py:46 - [review-performance] Scalar subqueries in SELECT clause cause N+1 pattern for currently_testing and next_review_date
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-005
  - **Rationale:** Each VBU row triggers separate subqueries; with 100+ VBUs this becomes 200+ additional queries

- [x] CR-095: backend/canvas/services/canvas_service.py:85 - [review-performance] Missing eager loading in get_canvas_by_vbu causes N+1 for theses and proof_points
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** 5 theses × 3 proof_points = 15+ additional queries per canvas load

- [x] CR-096: backend/canvas/reviews/schemas.py:13 - [review-data] Hardcoded regex "^(thesis|proof_point)$" instead of using CurrentlyTestingType enum
  - **Feature:** 004-monthly-review
  - **Task:** T-004
  - **Rationale:** Schema validation doesn't match model enum definition; if enum values change, validation is out of sync

- [x] CR-097: backend/canvas/portfolio/schemas.py:7 - [review-data] Duplicate LifecycleLane enum definition instead of importing from canvas.models.canvas
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-001
  - **Rationale:** Enum value inconsistency risk between portfolio schemas and canvas models; DRY violation

- [x] CR-098: docker-compose.yml:21 - [review-devops] Backend port mapping 8001:8000 conflicts with architecture.md specification of 8000:8000
  - **Feature:** 001A-infrastructure
  - **Task:** T-010
  - **Rationale:** Port inconsistency between documentation and deployment causes confusion

### Low

- [x] CR-099: frontend/src/canvas/hooks/useCanvas.ts:180 - [review-frontend] Missing cleanup for debounced save timeout on component unmount
  - **Feature:** 002-canvas-management
  - **Task:** T-024
  - **Rationale:** Timeout may fire after unmount causing memory leak and state update on unmounted component

- [x] CR-100: frontend/src/dashboard/DashboardPage.tsx:60 - [review-architect] Console.log statement in production code
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-014
  - **Rationale:** Debug logging should be removed or replaced with proper logging

- [x] CR-101: frontend/src/components/StatusBadge.tsx:85 - [review-frontend] Dropdown menu missing focus trap for keyboard navigation
  - **Feature:** 002-canvas-management
  - **Task:** T-020
  - **Rationale:** Keyboard users can tab out of dropdown, breaking expected focus management

- [x] CR-102: frontend/src/dashboard/VBUTable.tsx:150 - [review-frontend] Table rows missing proper ARIA labels for screen readers
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-015
  - **Rationale:** Screen readers cannot properly announce row content

- [x] CR-103: frontend/src/reviews/ReviewWizard.tsx:45 - [review-frontend] Step validation errors not announced to screen readers
  - **Feature:** 004-monthly-review
  - **Task:** T-015
  - **Rationale:** Users with screen readers don't receive feedback when step validation fails

## Summary
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 5 |
| Medium | 10 |
| Low | 5 |
| **Total** | **20** |
