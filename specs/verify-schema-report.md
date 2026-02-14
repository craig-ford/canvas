# Verify Schema Report

## Summary
| Feature | 1C | 1D | Status |
|---------|----|----|--------|
| 001A-infrastructure | ✓ | ✓ | PASS |
| 001-auth | ✗ | ✓ | FAIL |
| 002-canvas-management | ✗ | ✓ | FAIL |
| 003-portfolio-dashboard | ✓ | ✓ | PASS |
| 004-monthly-review | ✗ | ✓ | FAIL |

## Entity Mismatches (1C)
| Feature | Entity | Field | Spec Says | Schema Says |
|---------|--------|-------|-----------|-------------|
| 001-auth | User | email | String(255) | VARCHAR(255) |
| 001-auth | User | password_hash | String(255) | VARCHAR(255) |
| 001-auth | User | name | String(255) | VARCHAR(255) |
| 001-auth | User | is_active | Boolean, server_default=text('true') | BOOLEAN, default True |
| 001-auth | User | failed_login_attempts | Integer, server_default=text('0') | INTEGER, default 0 |
| 002-canvas-management | VBU | name | String(255) | VARCHAR(255) |
| 002-canvas-management | VBU | gm_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | VBU | updated_by | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Canvas | vbu_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Canvas | product_name | String(255) | VARCHAR(255) |
| 002-canvas-management | Canvas | primary_focus | String(255) | VARCHAR(255) |
| 002-canvas-management | Canvas | currently_testing_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Canvas | updated_by | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Thesis | canvas_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Thesis | order | Integer | INTEGER |
| 002-canvas-management | Thesis | text | Text | TEXT |
| 002-canvas-management | ProofPoint | thesis_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | ProofPoint | description | Text | TEXT |
| 002-canvas-management | ProofPoint | status | Enum(ProofPointStatus) | ENUM('not_started','in_progress','observed','stalled') |
| 002-canvas-management | ProofPoint | evidence_note | Text | TEXT |
| 002-canvas-management | Attachment | proof_point_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Attachment | monthly_review_id | UUID(as_uuid=True) | UUID |
| 002-canvas-management | Attachment | filename | String(255) | VARCHAR(255) |
| 002-canvas-management | Attachment | storage_path | String(1024) | VARCHAR(1024) |
| 002-canvas-management | Attachment | content_type | String(128) | VARCHAR(128) |
| 002-canvas-management | Attachment | size_bytes | Integer | INTEGER |
| 002-canvas-management | Attachment | label | String(255) | VARCHAR(255) |
| 002-canvas-management | Attachment | uploaded_by | UUID(as_uuid=True) | UUID |
| 004-monthly-review | MonthlyReview | canvas_id | UUID(as_uuid=True) | UUID |
| 004-monthly-review | MonthlyReview | what_moved | Text | TEXT |
| 004-monthly-review | MonthlyReview | what_learned | Text | TEXT |
| 004-monthly-review | MonthlyReview | what_threatens | Text | TEXT |
| 004-monthly-review | MonthlyReview | currently_testing_id | UUID(as_uuid=True) | UUID |
| 004-monthly-review | MonthlyReview | created_by | UUID(as_uuid=True) | UUID |
| 004-monthly-review | Commitment | monthly_review_id | UUID(as_uuid=True) | UUID |
| 004-monthly-review | Commitment | text | Text | TEXT |
| 004-monthly-review | Commitment | order | Integer | INTEGER |

## Contradictions Found (1D)
None

## Overall: 2 PASS, 3 FAIL