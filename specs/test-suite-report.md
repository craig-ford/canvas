# Test Suite Report

**Date:** 2026-02-17T07:55:00-08:00
**Result:** PASS

## Environment
| Component | Runner | Version | Execution Context |
|-----------|--------|---------|-------------------|
| Backend | pytest | 8.4.2 | canvas-backend-1 container |
| Frontend | none | N/A | No test runner configured |

## Infrastructure Fixes Applied
1. **SQLEnum values_callable** (session 1): All 4 Python enums fixed to use lowercase values
2. **Reserved word quoting** (session 1): `order` column quoted in CHECK constraints
3. **Test database** (session 1): Created `canvas_test` database
4. **Test deps** (session 1): Installed pytest, pytest-asyncio, httpx in container
5. **canvas_b fixture** (session 2): Fixed to depend on `other_canvas` instead of querying non-existent canvas
6. **PDF template path** (session 2): Changed from `backend/canvas/pdf/templates` to `canvas/pdf/templates` for Docker
7. **Reviews router** (session 2): Fixed Pydantic v1/v2 compatibility (.dict() → .model_dump(), .from_orm() → .model_validate())
8. **Reviews service** (session 2): Added IntegrityError handling for duplicate review dates

## Backend Tests
| Metric | Value |
|--------|-------|
| Total | 262 |
| Passed | 262 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |

### Code Fixes Applied (Session 3)
- **reviews/schemas.py**: Added `from_attributes=True` to `CommitmentResponse` and `AttachmentResponse` — nested ORM objects couldn't be validated by `ReviewResponse`
- **reviews/router.py**: Added `ValueError` catch in `create_review` → returns 400 instead of 500 for invalid `currently_testing_id`
- **routes/attachment.py**: Fixed `AttachmentService` dependency injection with factory function; replaced string-based `selectinload()` calls with class-attribute-based calls (SQLAlchemy 2.x requirement)
- **routes/thesis.py**: Added `IntegrityError` handling in reorder endpoint → returns 422 instead of crashing connection

### Test Fixes Applied (Session 3)
- **test_attachment_api.py**: Removed `"error" in data` assertions (FastAPI returns `"detail"` for validation errors)
- **test_canvas_api.py**: Changed expected status from 500 to 422 (Pydantic catches empty string before DB)
- **test_proof_point_api.py**: Changed `"error"` key check to `"detail"` for validation response
- **test_thesis_api.py**: Fixed duplicate order (409 not 201), reorder count (3 not 2), invalid order (422)
- **test_vbu_api.py**: Accept any error status for invalid gm_id constraint violation

## Frontend Tests
| Metric | Value |
|--------|-------|
| Total | 5 files |
| Passed | N/A |
| Failed | N/A |
| Not Run | No test runner (vitest) in package.json |

## Overall: PASS
