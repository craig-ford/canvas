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
| 001-auth | User | role | ENUM(UserRole), default=UserRole.VIEWER | ENUM('admin','gm','viewer'), default 'viewer' |
| 002-canvas-management | Attachment | content_type | CHECK content_type IN ('image/png','image/jpeg','image/gif','application/pdf','text/csv','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') | CHECK content_type IN ('image/jpeg','image/png','image/gif','application/pdf','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','application/vnd.openxmlformats-officedocument.wordprocessingml.document','application/vnd.openxmlformats-officedocument.presentationml.presentation') |
| 004-monthly-review | MonthlyReview | currently_testing_type | ENUM("thesis", "proof_point", name="testing_type") | ENUM('thesis','proof_point') |
| 004-monthly-review | Commitment | text | CHECK(length(text) > 0 AND length(text) <= 1000) | CHECK(length(text) BETWEEN 1 AND 1000) |

## Contradictions Found (1D)
None

## Overall: 2 PASS, 3 FAIL