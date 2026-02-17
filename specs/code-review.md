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
