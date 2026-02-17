# Test Suite Report

**Date:** 2026-02-17T08:58:00-08:00
**Result:** PASS

## Summary
- Backend: 275 passed, 0 failed, 0 errors, 0 skipped
- Frontend: Not applicable (no vitest runner)
- Duration: 103s

## Attempt History
| Attempt | Passed | Failed | Errors | Notes |
|---------|--------|--------|--------|-------|
| 1 (pre-code-review) | 262 | 0 | 0 | All passing before code review |
| 2 (post-fix-mode) | 256 | 19 | 0 | Fix agents introduced 19 failures |
| 3 (this run) | 275 | 0 | 0 | All resolved |

## Code Fixes Applied
1. `backend/canvas/portfolio/service.py`: Fixed invalid `func.INTERVAL` ORM syntax → `text("INTERVAL '1 month'")` (review-security agent broke this)
2. `backend/canvas/services/canvas_service.py`: Restored working `reorder_theses` with constraint drop/recreate pattern (review-security agent broke atomic reorder)

## Test Fixes Applied
1. Reviews API tests (4): Added missing CSRF token headers
2. Auth rate limiting test (1): Updated to expect 429, clear rate_limit_store before test
3. Canvas API tests (2): Updated status code expectations (422 instead of 500)
4. Thesis API tests (3): Updated for working reorder (200) and proper validation codes (409, 422)
5. Proof point test (1): Updated response shape expectation ('detail' not 'error')
6. VBU test (1): Updated status code (422 instead of 500)
7. PDF service tests (3): Added mock db parameter to PDFService constructor

## Infrastructure Fixes
None required — test infrastructure was already bootstrapped from previous runs.
