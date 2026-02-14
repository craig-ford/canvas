# Verify Schema Report

## Summary
| Feature | 1C | 1D | Status |
|---------|----|----|--------|
| 001A-infrastructure | N/A | N/A | N/A |
| 001-auth | ✓ | ✓ | PASS |
| 002-canvas-management | ✗ | ✓ | FAIL |
| 003-portfolio-dashboard | N/A | N/A | N/A |
| 004-monthly-review | ✗ | ✓ | FAIL |

## Entity Mismatches (1C)
| Feature | Entity | Field | Spec Says | Schema Says |
|---------|--------|-------|-----------|-------------|
| 002-canvas-management | VBU | name | CHECK(LENGTH(TRIM(name)) > 0) | NOT NULL |
| 002-canvas-management | VBU | gm_id | FK → users.id ON DELETE RESTRICT | FK → users.id |
| 002-canvas-management | VBU | updated_by | FK → users.id ON DELETE SET NULL | FK → users.id |
| 002-canvas-management | Canvas | vbu_id | FK → vbus.id ON DELETE CASCADE | FK → vbus.id |
| 002-canvas-management | Canvas | product_name | CHECK(product_name IS NULL OR LENGTH(TRIM(product_name)) > 0) | NULLABLE |
| 002-canvas-management | Canvas | updated_by | FK → users.id ON DELETE SET NULL | FK → users.id |
| 002-canvas-management | Thesis | canvas_id | FK → canvases.id ON DELETE CASCADE | FK → canvases.id |
| 002-canvas-management | Thesis | order | CHECK(order BETWEEN 1 AND 5) | CHECK(1-5) |
| 002-canvas-management | Thesis | text | CHECK(LENGTH(TRIM(text)) > 0) | NOT NULL |
| 002-canvas-management | ProofPoint | thesis_id | FK → theses.id ON DELETE CASCADE | FK → theses.id |
| 002-canvas-management | ProofPoint | description | CHECK(LENGTH(TRIM(description)) > 0) | NOT NULL |
| 002-canvas-management | Attachment | proof_point_id | FK → proof_points.id ON DELETE CASCADE | FK → proof_points.id |
| 002-canvas-management | Attachment | monthly_review_id | FK → monthly_reviews.id ON DELETE CASCADE | FK → monthly_reviews.id |
| 002-canvas-management | Attachment | filename | CHECK(LENGTH(TRIM(filename)) > 0) | NOT NULL |
| 002-canvas-management | Attachment | storage_path | CHECK(LENGTH(TRIM(storage_path)) > 0) | UNIQUE, NOT NULL |
| 002-canvas-management | Attachment | label | CHECK(label IS NULL OR LENGTH(TRIM(label)) > 0) | NULLABLE |
| 002-canvas-management | Attachment | uploaded_by | FK → users.id ON DELETE RESTRICT | FK → users.id |
| 004-monthly-review | MonthlyReview | canvas_id | FK → canvases.id ON DELETE CASCADE | FK → canvases.id |
| 004-monthly-review | MonthlyReview | created_by | FK → users.id ON DELETE RESTRICT | FK → users.id |
| 004-monthly-review | Commitment | monthly_review_id | FK → monthly_reviews.id ON DELETE CASCADE | FK → monthly_reviews.id |
| 004-monthly-review | Commitment | order | CHECK(order BETWEEN 1 AND 3) | CHECK(1-3) |

## Contradictions Found (1D)
None

## Overall: 2 PASS, 2 FAIL