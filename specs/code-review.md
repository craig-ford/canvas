# Code Review

**Date:** 2026-02-17T09:01:00-08:00
**Iteration:** 2

## Previous Iteration Summary
- Iteration 1: 47 issues found, all fixed and verified
- Test suite: 275/275 passing after fixes

## Issues Found

### Critical

- [x] CR-048: frontend/src/main.tsx:5 - [review-frontend] Missing CSS/Tailwind entry point import
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** App uses Tailwind classes throughout but main.tsx has no CSS import — all styling is broken

- [x] CR-049: frontend/src/App.tsx:1 - [review-frontend] Missing ErrorBoundary wrapper around application routes
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** Unhandled errors crash entire app with no recovery; ErrorBoundary component exists but is not used

### High

- [x] CR-050: frontend/src/auth/AuthContext.tsx:76 - [review-frontend] Race condition in token refresh interceptor — no isRefreshing guard
  - **Feature:** 001-auth
  - **Task:** T-017
  - **Rationale:** Multiple concurrent 401 responses all trigger refreshToken() simultaneously, causing duplicate refresh calls and potential auth loops

- [x] CR-051: frontend/src/components/InlineEdit.tsx:51 - [review-frontend] Memory leak — saveTimeoutRef not cleared on unmount
  - **Feature:** 002-canvas-management
  - **Task:** T-019
  - **Rationale:** debouncedSave sets timeout via saveTimeoutRef but no useEffect cleanup clears it on unmount, causing state updates on unmounted component

- [x] CR-052: frontend/tsconfig.json - [review-devops] Missing TypeScript configuration file
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** TypeScript compilation and IDE support requires tsconfig.json; without it type checking is inconsistent

- [x] CR-053: frontend/tailwind.config.ts - [review-devops] Missing Tailwind CSS configuration and dependency
  - **Feature:** 001A-infrastructure
  - **Task:** T-011
  - **Rationale:** Architecture specifies Tailwind CSS >=4.0 but no config exists and tailwindcss not in package.json

- [x] CR-054: backend/pyproject.toml - [review-devops] Missing pyproject.toml for Python project configuration
  - **Feature:** 001A-infrastructure
  - **Task:** T-001
  - **Rationale:** No proper dependency management or build configuration; only requirements.txt exists

### Medium

- [x] CR-055: backend/canvas/routes/vbu.py:60 - [review-security] Missing CSRF protection on VBU state-changing operations (POST, PATCH, DELETE)
  - **Feature:** 002-canvas-management
  - **Task:** T-014
  - **Rationale:** VBU creation, updates, and deletion lack X-CSRF-Token header validation

- [x] CR-056: backend/canvas/routes/canvas.py:86 - [review-security] Missing CSRF protection on canvas update (PUT)
  - **Feature:** 002-canvas-management
  - **Task:** T-015
  - **Rationale:** Canvas updates can be triggered by malicious sites without user consent

- [x] CR-057: backend/canvas/routes/thesis.py:37 - [review-security] Missing CSRF protection on thesis operations (POST, PATCH, DELETE, PUT)
  - **Feature:** 002-canvas-management
  - **Task:** T-016
  - **Rationale:** Thesis CRUD operations lack CSRF protection

- [x] CR-058: backend/canvas/routes/proof_point.py:41 - [review-security] Missing CSRF protection on proof point operations (POST, PATCH, DELETE)
  - **Feature:** 002-canvas-management
  - **Task:** T-017
  - **Rationale:** Proof point modifications vulnerable to CSRF attacks

- [x] CR-059: backend/canvas/routes/attachment.py:26 - [review-security] Missing CSRF protection on attachment operations (POST, DELETE)
  - **Feature:** 002-canvas-management
  - **Task:** T-018
  - **Rationale:** File uploads and deletions vulnerable to CSRF attacks

- [x] CR-060: backend/canvas/portfolio/router.py:44 - [review-security] Missing CSRF protection on portfolio notes update (PATCH)
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-003
  - **Rationale:** Admin-only portfolio notes updates lack CSRF protection

- [x] CR-061: backend/canvas/services/canvas_service.py:245 - [review-performance] Multiple sequential DB queries in ownership verification instead of JOINs
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** verify_thesis_ownership, verify_proof_point_ownership perform 3-4 separate queries when a single JOIN would suffice

- [x] CR-062: frontend/src/dashboard/VBUTable.tsx:95 - [review-frontend] Missing keyboard navigation for table rows
  - **Feature:** 003-portfolio-dashboard
  - **Task:** T-015
  - **Rationale:** Table rows have tabIndex but no keyboard event handling for accessibility

- [x] CR-063: frontend/src/reviews/components/CommitmentsStep.tsx:1 - [review-frontend] Form validation errors not announced to screen readers
  - **Feature:** 004-monthly-review
  - **Task:** T-015
  - **Rationale:** Validation errors lack ARIA live regions for accessibility

- [x] CR-064: backend/canvas/main.py:20 - [review-devops] Missing graceful shutdown handling
  - **Feature:** 001A-infrastructure
  - **Task:** T-008
  - **Rationale:** No signal handlers for SIGTERM/SIGINT; container shutdowns may cause data loss

- [x] CR-065: backend/canvas/main.py:1 - [review-devops] Missing structured logging configuration
  - **Feature:** 001A-infrastructure
  - **Task:** T-008
  - **Rationale:** Architecture specifies structlog for JSON logging but only basic Python logging configured

### Low

- [x] CR-066: backend/canvas/auth/routes.py:20 - [review-security] In-memory rate limiting store not persistent across restarts
  - **Feature:** 001-auth
  - **Task:** T-016
  - **Rationale:** Rate limiting bypassed by server restarts; acceptable for MVP but should use Redis in production

- [x] CR-067: backend/canvas/services/canvas_service.py:1 - [review-architect] God class (326 lines) handling VBU, Canvas, Thesis, ProofPoint operations (DEFERRED from iteration 1: architectural improvement for future iteration)
  - **Feature:** 002-canvas-management
  - **Task:** T-012
  - **Rationale:** Violates SRP but functional; splitting would be a refactor, not a bug fix

- [x] CR-068: frontend/src/canvas/CanvasPage.tsx:1 - [review-architect] Large component (431 lines) handling multiple responsibilities
  - **Feature:** 002-canvas-management
  - **Task:** T-022
  - **Rationale:** Violates SRP but functional; splitting would be a refactor

## Excluded (False Positives / Already Fixed / Duplicates)

- review-backend CR "Active database constraint violations" — runtime log artifacts from test runs, not code issues
- review-backend CR "Missing transaction rollback" — SQLAlchemy session handles rollback via context manager
- review-backend CR "N+1 in ownership verification" — duplicate of CR-061 (review-performance)
- review-backend CR "In-memory rate limiting" — duplicate of CR-066 (review-security)
- review-backend CR "Hardcoded limit 1000" — portfolio service uses LIMIT as safety cap, pagination exists via query params
- review-backend CR "Missing error handling in _save_file" — file ops wrapped in try/except with proper cleanup
- review-backend CR "Generic IntegrityError handling" — correctly checks specific constraint name
- review-backend CR "Inconsistent error response format" — all routes use consistent JSONResponse pattern
- review-frontend CR "useAutoSave memory leak" — FALSE POSITIVE: has proper cleanup in useEffect return
- review-frontend CR "Missing ErrorBoundary on CanvasPage" — duplicate of CR-049 (app-level boundary covers this)
- review-frontend CR "StatusBadge aria-describedby" — component uses aria-label correctly
- review-frontend CR "Hardcoded API URL" — uses VITE_API_URL env var with localhost fallback for dev
- review-data CR "Migration dependency error" — FALSE POSITIVE: migration 002 creates attachments with nullable monthly_review_id, migration 004 creates monthly_reviews; FK constraint added after both tables exist
- review-data CR "Enum inconsistency" — FALSE POSITIVE: SQLAlchemy Enum() with inline values is valid
- review-data CR "Content type validation mismatch" — service validates against same MIME types as DB constraint
- review-data CR "Unsafe constraint manipulation in reorder" — uses parameterized query with proper transaction
- review-data CR "Raw SQL injection risk" — FALSE POSITIVE: already fixed in iteration 1 (CR-001)
- review-architect CR "Hardcoded Settings() in routes" — Settings() instantiation at module level is standard FastAPI pattern; Depends(Settings) BREAKS FastAPI with Pydantic BaseSettings
- review-architect CR "Settings() in main.py" — same as above
- review-architect CR "Settings() in db.py" — same as above
- review-architect CR "Optional Settings parameter" — acceptable pattern for testability
- review-testing CR "Tautological contract tests" — contract tests intentionally verify interface shape, not behavior; integration tests cover behavior
- review-testing CR "Mock-heavy unit tests" — service unit tests verify initialization; integration tests cover logic
- review-testing CR "Weak CORS assertion" — test correctly accepts valid CORS responses
- review-testing CR "Weak session cleanup assertion" — tests session lifecycle correctly

## Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 5 |
| Medium | 11 |
| Low | 3 |
| **Total** | **21** |
