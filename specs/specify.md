# Canvas — Feature Breakdown

## Implementation Phases

### Phase 1: Foundation
Infrastructure and auth — everything else depends on these.

### Phase 2: Core
Canvas management — the primary user-facing feature.

### Phase 3: Views & Workflows
Portfolio dashboard and monthly review — consume canvas data.

## Dependency Graph

```
001A-infrastructure ──→ 001-auth ──→ 002-canvas-management ──┬──→ 003-portfolio-dashboard
                                                              └──→ 004-monthly-review
```

## Features

### 001A-infrastructure
**Phase:** 1 — Foundation
**Description:** Docker Compose (dev/prod), Dockerfiles, env files, database setup, Alembic scaffolding, FastAPI app factory with CORS/middleware/health endpoint, Pydantic config, async DB engine, response helpers, frontend scaffolding (Vite + React + Tailwind + Axios client + AppShell), seed data script.
**Dependencies:** None
**Estimated Tasks:** 8-12

### 001-auth
**Phase:** 1 — Foundation
**Description:** User authentication (register, login, JWT access/refresh tokens) and role-based access control (admin, gm, viewer). User model, auth service, JWT middleware, auth dependencies (`get_current_user`, `require_role`). Admin user management (list, update role, delete). Frontend login page and `useAuth` hook.
**Dependencies:** 001A-infrastructure
**Estimated Tasks:** 8-10

### 002-canvas-management
**Phase:** 2 — Core
**Description:** Full CRUD for VBUs, Canvases (1:1 with VBU), Theses (ordered, max 5), Proof Points (with status tracking), and Attachments (file upload/download). Inline editing with autosave on the frontend. VBU Canvas page with all sections: context, future state, lifecycle, theses, proof points, constraints, cadence. "Currently testing" pointer management.
**Dependencies:** 001-auth
**Estimated Tasks:** 12-15

### 003-portfolio-dashboard
**Phase:** 3 — Views & Workflows
**Description:** Aggregated portfolio view showing all VBUs with lifecycle lane, success description, currently testing, next review date, top constraint, and proof point health indicator. Filterable by lane, GM, health status. Portfolio notes panel (admin only). PDF export of individual canvases via WeasyPrint. Frontend dashboard page with VBU table, filters, and export button.
**Dependencies:** 002-canvas-management, 001-auth
**Estimated Tasks:** 8-10

### 004-monthly-review
**Phase:** 3 — Views & Workflows
**Description:** Guided 4-step monthly review wizard (what moved, what learned, what threatens, commitments + currently testing selection). Creates dated MonthlyReview entries with 1-3 Commitments. Updates canvas "currently testing" pointer on submit. Review history display on VBU Canvas page. File attachments on reviews.
**Dependencies:** 002-canvas-management, 001-auth
**Estimated Tasks:** 8-10

## Summary

| Metric | Value |
|--------|-------|
| Total Features | 5 (including infrastructure) |
| Estimated Total Tasks | 44-57 |
| Implementation Phases | 3 |
| Complexity Classification | Simple |
