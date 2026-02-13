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
| 001-auth | User | is_active | Boolean, NOT NULL, default=True | Not defined |
| 001-auth | User | last_login_at | DateTime(timezone=True), nullable=True | Not defined |
| 001-auth | User | failed_login_attempts | Integer, NOT NULL, default=0 | Not defined |
| 001-auth | User | locked_until | DateTime(timezone=True), nullable=True | Not defined |
| 002-canvas-management | Canvas | lifecycle_lane | default=LifecycleLane.BUILD | NOT NULL (no default specified) |
| 002-canvas-management | Attachment | storage_path | unique=True | NOT NULL (no unique constraint) |
| 002-canvas-management | Attachment | content_type | CheckConstraint with specific MIME types | VARCHAR(128), NOT NULL (no constraint) |
| 002-canvas-management | Attachment | size_bytes | CheckConstraint(1 to 10485760) | INTEGER, NOT NULL (no constraint) |
| 004-monthly-review | MonthlyReview | currently_testing_type | Enum("thesis", "proof_point") | ENUM('thesis','proof_point') |
| 004-monthly-review | Commitment | text | CheckConstraint(length 1-1000) | TEXT, NOT NULL (no length constraint) |
| 004-monthly-review | Commitment | order | CheckConstraint(1-3) | INTEGER, NOT NULL, CHECK(1-3) |

## Contradictions Found (1D)
None

## Overall: 2 PASS, 3 FAIL