# Canvas — Master Plan

## Implementation Order

### Phase 1: Foundation
| Feature | Status | Est. LOC | Est. Tasks |
|---------|--------|----------|------------|
| 001A-infrastructure | planned | ~580 | 12 |
| 001-auth | planned | ~1150 | 24 |

### Phase 2: Core
| Feature | Status | Est. LOC | Est. Tasks |
|---------|--------|----------|------------|
| 002-canvas-management | planned | ~2100 | 25 |

### Phase 3: Views & Workflows
| Feature | Status | Est. LOC | Est. Tasks |
|---------|--------|----------|------------|
| 003-portfolio-dashboard | planned | ~1750 | 24 |
| 004-monthly-review | planned | ~1250 | 18 |

## Totals
- **Total Estimated LOC:** ~6830
- **Total Estimated Tasks:** 103
- **Implementation Phases:** 3

## Dependency Graph
```
001A-infrastructure ──→ 001-auth ──→ 002-canvas-management ──┬──→ 003-portfolio-dashboard
                                                              └──→ 004-monthly-review
```

## Cross-Feature Contracts
- **AttachmentService** (owned by 002): consumed by 004
- **Auth dependencies** (owned by 001): consumed by 002, 003, 004
- **Response helpers** (owned by 001A): consumed by all
- **PDFService** (owned by 003): self-contained

## Parallel Opportunities
- 003 and 004 can execute in parallel (both depend on 002, no mutual dependency)
