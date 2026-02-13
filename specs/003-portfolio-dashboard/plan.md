# specs/003-portfolio-dashboard/plan.md

## Overview
Building an aggregated portfolio dashboard that displays all VBUs with strategic health indicators, filtering capabilities, and PDF export functionality. The core approach is a library-first design with optimized database queries for health indicator computation, role-based access control, and a responsive React frontend with autosave portfolio notes.

## Constitutional Gate Review

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | ✓ | PortfolioService and PDFService are standalone libraries, UI is thin veneer |
| CLI Mandate | ✓ | Libraries expose CLI with JSON stdout for portfolio summary and PDF export |
| Test-First | ✓ | Clear contracts exist for all services, tests written before implementation |
| Integration-First | ✓ | Real PostgreSQL database, no mocks for data layer |
| Simplicity Gate | ✓ | 3 entities (VBU, Canvas, ProofPoint), 3 endpoints, no premature abstraction |
| Single Domain Model | ✓ | Direct entity mapping, no DTOs except at serialization boundary |

## Dependencies

### Cross-Feature (from master-spec.md)
| Feature | What We Import | Status |
|---------|----------------|--------|
| 001-auth | get_current_user, require_role dependencies | Complete |
| 002-canvas-management | VBU, Canvas, Thesis, ProofPoint models | Complete |

### External Libraries
| Library | Version | Purpose |
|---------|---------|--------|
| WeasyPrint | >=62.0 | HTML-to-PDF canvas export |
| Jinja2 | >=3.1 | PDF template rendering |
| html | stdlib | XSS prevention for portfolio notes |

## Implementation Phases

### Phase 1: Contracts & Interfaces
- [ ] PortfolioService interface with get_summary and update_portfolio_notes methods
- [ ] PDFService interface with export_canvas method
- [ ] VBUSummary, PortfolioFilters, PortfolioNotesRequest Pydantic models
- [ ] CLI interfaces for portfolio summary and PDF export
Estimate: ~150 LOC

### Phase 2: Test Infrastructure
- [ ] Portfolio service contract tests (role-based filtering, health computation)
- [ ] PDF service contract tests (template rendering, file generation)
- [ ] API endpoint integration tests with real database
- [ ] Frontend component tests with React Testing Library
Estimate: ~300 LOC

### Phase 3: Data Layer
- [ ] Health indicator materialization: add health_indicator_cache column to canvases
- [ ] Database trigger for automatic health indicator updates on proof point changes
- [ ] Optimized indexes for portfolio dashboard query performance
- [ ] Migration script for health indicator cache population
Estimate: ~100 LOC

### Phase 4: Core Logic
- [ ] PortfolioService with optimized SQL queries and role-based filtering
- [ ] Health indicator computation logic (stalled → At Risk, all not_started → Not Started, etc.)
- [ ] PDFService with WeasyPrint integration and Canvas brand styling
- [ ] Portfolio notes update with HTML entity encoding for XSS prevention
Estimate: ~400 LOC

### Phase 5: API Layer
- [ ] GET /api/portfolio/summary with query parameter filtering
- [ ] PATCH /api/portfolio/notes with admin-only access control
- [ ] GET /api/vbus/{vbu_id}/canvas/pdf with proper file response headers
- [ ] Error handling and validation for all endpoints
Estimate: ~200 LOC

### Phase 6: UI
- [ ] DashboardPage with responsive layout (table/card/list breakpoints)
- [ ] VBUTable with sortable columns and pagination
- [ ] DashboardFilters with multi-select dropdowns
- [ ] PortfolioNotes with autosave and admin-only visibility
- [ ] HealthIndicator component with proper ARIA labels
- [ ] PDF export functionality with download handling
Estimate: ~600 LOC

## Parallel Work Opportunities
- Phase 3 (Data Layer) and Phase 4 (Core Logic) can run concurrently
- Phase 5 (API Layer) and Phase 6 (UI) can start once Phase 4 is complete
- PDF template development can happen in parallel with service implementation

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| WeasyPrint performance issues with complex canvases | Medium | High | Implement caching, optimize HTML template, set 5s timeout |
| Health indicator computation performance at scale | Medium | Medium | Materialized health_indicator_cache column with triggers |
| Portfolio notes XSS vulnerability | Low | High | HTML entity encoding, input validation, CSP headers |
| Role-based access control bypass | Low | High | Database-level filtering, comprehensive auth tests |

## Total Estimate
~1750 LOC across 24 tasks