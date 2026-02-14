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
| 001-auth | User | role | Enum('admin','gm','viewer', name='user_role_enum') | ENUM('admin','gm','viewer') |
| 001-auth | User | is_active | default=True | NOT NULL, default True |
| 001-auth | User | last_login_at | DateTime(timezone=True) | TIMESTAMPTZ |
| 001-auth | User | locked_until | DateTime(timezone=True) | TIMESTAMPTZ |
| 002-canvas-management | Canvas | lifecycle_lane | Enum(LifecycleLane), default=LifecycleLane.BUILD | ENUM('build','sell','milk','reframe'), default 'build' |
| 002-canvas-management | Canvas | currently_testing_type | Enum(CurrentlyTestingType) | ENUM('thesis','proof_point') |
| 002-canvas-management | Attachment | content_type | CheckConstraint with content_type IN (...) | CHECK(content_type IN ('image/jpeg',...)) |
| 004-monthly-review | MonthlyReview | currently_testing_type | Enum('thesis','proof_point', name='testing_type_enum') | ENUM('thesis','proof_point') |
| 004-monthly-review | Commitment | text | CheckConstraint("length(text) BETWEEN 1 AND 1000") | CHECK(length(text) BETWEEN 1 AND 1000) |

## Contradictions Found (1D)
None

## Overall: 2 PASS, 3 FAIL