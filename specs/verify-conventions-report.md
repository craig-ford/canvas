# Verify Conventions Report

## URL Pattern (from architecture.md)
```
/api/auth/{action}                    # Auth endpoints (no versioning)
/api/{resource}                       # List, Create
/api/{resource}/{id}                  # Retrieve, Update, Delete
/api/{parent}/{parent_id}/{resource}  # Nested resources
```

## Summary
| Feature | 3F Ambig | 3J URLs | Status |
|---------|----------|---------|--------|
| 001A-infrastructure | ✗ | ✓ | FAIL |
| 001-auth | ✓ | ✓ | PASS |
| 002-canvas-management | ✗ | ✓ | FAIL |
| 003-portfolio-dashboard | ✓ | ✗ | FAIL |
| 004-monthly-review | ✓ | ✓ | PASS |

## Ambiguities Found (3F)
| Feature | Task | Section | Text |
|---------|------|---------|------|
| 001A-infrastructure | T-008 | Logic | "Handle cleanup errors gracefully" |
| 002-canvas-management | T-013 | Logic | "File operations are atomic and handle errors" |

## URL Violations (3J)
| Feature | Task | Endpoint | Expected |
|---------|------|----------|----------|
| 003-portfolio-dashboard | T-007 | `/portfolio/summary` | `/api/portfolio/summary` |
| 003-portfolio-dashboard | T-007 | `/portfolio/notes` | `/api/portfolio/notes` |
| 003-portfolio-dashboard | T-008 | `/vbus/{vbu_id}/canvas/pdf` | `/api/vbus/{vbu_id}/canvas/pdf` |

## Overall: 2 PASS, 3 FAIL