# specs/003-portfolio-dashboard/tasks.md

## Progress
Total: 18 tasks | Complete: 5 | Remaining: 13

## Tasks
- [x] **T-001: Portfolio Service Contract Tests** - Define and test PortfolioService interface with get_summary and update_portfolio_notes methods | deps: none
- [x] **T-002: PDF Service Contract Tests** - Define and test PDFService interface with export_canvas method | deps: none
- [x] **T-003: Portfolio API Contract Tests** - Test portfolio endpoints with role-based access and filtering | deps: T-001
- [x] **T-004: Health Indicator Database Schema** - Add health_indicator_cache column and update trigger to canvases table | deps: none
- [x] **T-005: Portfolio Service Implementation** - Implement PortfolioService with optimized queries and health computation | deps: T-001, T-004
- [x] **T-006: PDF Service Implementation** - Implement PDFService with WeasyPrint and Canvas template | deps: T-002
- [ ] **T-007: Portfolio API Routes** - Implement GET /api/portfolio/summary and PATCH /api/portfolio/notes endpoints | deps: T-003, T-005
- [ ] **T-008: Canvas PDF Export Route** - Implement GET /api/vbus/{vbu_id}/canvas/pdf endpoint | deps: T-006
- [x] **T-009: Dashboard Page Component Tests** - Test DashboardPage with responsive layout and loading states | deps: none
- [x] **T-010: VBU Table Component Tests** - Test VBUTable with sorting, pagination, and accessibility | deps: none
- [x] **T-011: Dashboard Filters Component Tests** - Test DashboardFilters with multi-select and URL parameter sync | deps: none
- [x] **T-012: Portfolio Notes Component Tests** - Test PortfolioNotes with autosave and admin-only access | deps: none
- [x] **T-013: Health Indicator Component Tests** - Test HealthIndicator with proper ARIA labels and status mapping | deps: none
- [ ] **T-014: Dashboard Page Implementation** - Implement DashboardPage with responsive breakpoints and data fetching | deps: T-009
- [x] **T-015: VBU Table Implementation** - Implement VBUTable with sortable columns and pagination | deps: T-010
- [ ] **T-016: Dashboard Filters Implementation** - Implement DashboardFilters with multi-select dropdowns | deps: T-011
- [ ] **T-017: Portfolio Notes Implementation** - Implement PortfolioNotes with debounced autosave | deps: T-012
- [x] **T-018: Health Indicator Implementation** - Implement HealthIndicator with status badges and accessibility | deps: T-013

## Success Criteria
- ⬜ All tests pass
- ⬜ No lint errors
- ⬜ Feature works end-to-end
- ⬜ Portfolio summary loads <200ms for 50 VBUs
- ⬜ PDF export completes <2s for typical canvas
- ⬜ Role-based access control enforced
- ⬜ Responsive design works across breakpoints
- ⬜ Portfolio notes autosave with admin-only access