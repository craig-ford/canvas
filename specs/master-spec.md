# Canvas — Master Specification

## Features

| Feature | Phase | Dependencies | Status |
|---------|-------|-------------|--------|
| 001A-infrastructure | 1 - Foundation | None | spec ✅ |
| 001-auth | 1 - Foundation | 001A-infrastructure | spec ✅ |
| 002-canvas-management | 2 - Core | 001-auth | spec ✅ |
| 003-portfolio-dashboard | 3 - Views & Workflows | 002-canvas-management, 001-auth | spec ✅ |
| 004-monthly-review | 3 - Views & Workflows | 002-canvas-management, 001-auth | spec ✅ |

## Dependency Graph

```
001A-infrastructure ──→ 001-auth ──→ 002-canvas-management ──┬──→ 003-portfolio-dashboard
                                                              └──→ 004-monthly-review
```

## Shared Components

| Component | Owner | Consumers |
|-----------|-------|-----------|
| get_current_user / require_role | 001-auth | 002, 003, 004 |
| success_response / list_response | 001A-infrastructure | all |
| AttachmentService | 002-canvas-management | 004-monthly-review |
| PDFService | 003-portfolio-dashboard | 003-portfolio-dashboard |
| TimestampMixin (base model) | 001A-infrastructure | all |
| API client (Axios) | 001A-infrastructure | all frontend |
| AppShell | 001A-infrastructure | all frontend |
| useAuth hook | 001-auth | all frontend |

## Data Model Summary

| Entity | Owner Feature | Table |
|--------|--------------|-------|
| User | 001-auth | users |
| VBU | 002-canvas-management | vbus |
| Canvas | 002-canvas-management | canvases |
| Thesis | 002-canvas-management | theses |
| ProofPoint | 002-canvas-management | proof_points |
| MonthlyReview | 004-monthly-review | monthly_reviews |
| Commitment | 004-monthly-review | commitments |
| Attachment | 002-canvas-management | attachments |
