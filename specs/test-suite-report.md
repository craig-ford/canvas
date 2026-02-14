# Test Suite Report

**Date:** 2026-02-14T13:57:00-08:00
**Result:** FAIL

## Environment
| Component | Runner | Version | Execution Context |
|-----------|--------|---------|-------------------|
| Backend | pytest | 9.0.2 | canvas-backend-1 container |
| Frontend | none | N/A | No test runner configured |

## Infrastructure Fixes Applied
1. **SQLEnum values_callable**: All 4 Python enums (UserRole, LifecycleLane, CurrentlyTestingType, ProofPointStatus) used `SQLEnum(EnumClass)` which registered uppercase NAMES (ADMIN, GM, VIEWER) as PostgreSQL enum values instead of lowercase values (admin, gm, viewer). Fixed with `values_callable=lambda e: [x.value for x in e]`.
2. **Reserved word quoting**: `order` column in Thesis and Commitment models used unquoted `order` in CHECK constraints, causing PostgreSQL syntax errors. Fixed by quoting as `"order"`.
3. **Test database**: Created `canvas_test` database for test isolation.
4. **Test deps**: Installed pytest, pytest-asyncio, httpx in container (not in Dockerfile — needs permanent fix).

## Backend Tests
| Metric | Value |
|--------|-------|
| Total | 266 |
| Passed | 127 |
| Failed | 50 |
| Errors | 89 |
| Skipped | 0 |

### Error Categories (89 errors — fixture setup failures)
Missing fixtures used by tests that don't exist in conftest.py:
- `test_canvas`, `test_vbu`, `test_thesis` — should use `sample_canvas`, `sample_vbu`
- `gm_canvas`, `gm_vbu`, `gm_thesis` — need GM-scoped data fixtures
- `own_canvas`, `other_canvas`, `other_vbu` — need multi-user data fixtures
- `canvas_with_theses`, `canvas_with_proof_points` — need composite fixtures
- `canvas`, `review`, `sample_thesis`, `sample_user` — various aliases
- `canvas_a`, `canvas_with_multiple_theses`, `other_canvas_thesis` — complex fixtures
- `any_canvas`, `other_canvas_with_theses` — authorization test fixtures

### Failure Categories (50 failures — assertion mismatches)
- **Auth route integration** (8): Tests expect specific response shapes/status codes that don't match actual API responses
- **User management routes** (10): Tests use wrong API paths or expect different response formats
- **User service** (4): Tests expect different method signatures or error types
- **Attachment API/service** (4): Tests expect different error handling patterns
- **Canvas/VBU/Thesis/ProofPoint API** (4): Tests expect different validation error formats
- **Monthly review relationships** (8): Tests expect different cascade/constraint behavior
- **Review API/service/commitment** (12): Tests expect different service method signatures

### Root Cause
Tests were generated from specs during execute phase but use fixture names and API response shapes that don't match the actual implementation. The conftest.py provides `sample_canvas`, `sample_vbu`, `sample_review` but tests reference `test_canvas`, `gm_canvas`, `own_canvas`, etc.

### Fix Strategy
1. Add missing fixtures to conftest.py (aliases + composite fixtures)
2. Fix test assertions to match actual API response shapes
3. Fix test API paths to match actual route registrations

## Frontend Tests
| Metric | Value |
|--------|-------|
| Total | 5 files |
| Passed | N/A |
| Failed | N/A |
| Not Run | No test runner (vitest/jest) in package.json |

### Fix Needed
Add vitest to frontend devDependencies and create test script.

## Overall: FAIL
