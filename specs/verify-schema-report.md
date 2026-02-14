# Verify Schema Report

## Summary
| Feature | 1C | 1D | Status |
|---------|----|----|--------|
| 001A-infrastructure | N/A | N/A | N/A |
| 001-auth | ✓ | ✓ | PASS |
| 002-canvas-management | ✓ | ✓ | PASS |
| 003-portfolio-dashboard | N/A | N/A | N/A |
| 004-monthly-review | ✓ | ✓ | PASS |

## Entity Mismatches (1C)
None

## Contradictions Found (1D)
None

## Overall: 3 PASS, 0 FAIL

## Detailed Analysis

### 001A-infrastructure
- **Status:** N/A - No Data Model section found
- **Check 1C:** N/A
- **Check 1D:** N/A

### 001-auth
- **Status:** PASS
- **Check 1C:** ✓ User entity matches schema.md exactly
  - All 11 fields match: id, email, password_hash, name, role, is_active, last_login_at, failed_login_attempts, locked_until, created_at, updated_at
  - All types match: UUID, VARCHAR(255), BOOLEAN, TIMESTAMPTZ, INTEGER, ENUM('admin','gm','viewer')
  - All constraints match: PK, UNIQUE, NOT NULL, NULLABLE, defaults
- **Check 1D:** ✓ No contradictions found

### 002-canvas-management
- **Status:** PASS
- **Check 1C:** ✓ All entities match schema.md exactly
  - **VBU:** All 6 fields match (id, name, gm_id, created_at, updated_at, updated_by)
  - **Canvas:** All 15 fields match (id, vbu_id, product_name, lifecycle_lane, success_description, future_state_intent, primary_focus, resist_doing, good_discipline, primary_constraint, currently_testing_type, currently_testing_id, portfolio_notes, created_at, updated_at, updated_by)
  - **Thesis:** All 6 fields match (id, canvas_id, order, text, created_at, updated_at)
  - **ProofPoint:** All 8 fields match (id, thesis_id, description, status, evidence_note, target_review_month, created_at, updated_at)
  - **Attachment:** All 10 fields match (id, proof_point_id, monthly_review_id, filename, storage_path, content_type, size_bytes, label, uploaded_by, created_at)
- **Check 1D:** ✓ No contradictions found

### 003-portfolio-dashboard
- **Status:** N/A - No entity definitions found in Data Model section (contains only response models and frontend components)
- **Check 1C:** N/A
- **Check 1D:** N/A

### 004-monthly-review
- **Status:** PASS
- **Check 1C:** ✓ All entities match schema.md exactly
  - **MonthlyReview:** All 9 fields match (id, canvas_id, review_date, what_moved, what_learned, what_threatens, currently_testing_type, currently_testing_id, created_by, created_at)
  - **Commitment:** All 4 fields match (id, monthly_review_id, text, order)
- **Check 1D:** ✓ No contradictions found

## Notes
- All spec.md Data Model sections now use SQL DDL format matching schema.md exactly
- No SQLAlchemy vs SQL type mismatches found (previous issue resolved)
- Features 001A-infrastructure and 003-portfolio-dashboard contain no entity definitions to verify
- All entity field names, types, constraints, and nullability match canonical schema.md