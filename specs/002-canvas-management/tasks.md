# specs/002-canvas-management/tasks.md

## Progress
Total: 25 tasks | Complete: 11 | Remaining: 14

## Tasks
- [x] **T-001: Model Contract Tests** - Define SQLAlchemy models with relationships and constraints | deps: none
- [x] **T-002: Service Contract Tests** - Define CanvasService and AttachmentService interfaces | deps: none
- [x] **T-003: Model Implementation** - Implement VBU, Canvas, Thesis, ProofPoint, Attachment models | deps: T-001
- [x] **T-004: Database Migration** - Create Alembic migration for canvas management tables | deps: T-003
- [x] **T-005: CanvasService Integration Tests** - Test canvas CRUD operations with real database | deps: T-002, T-004
- [x] **T-006: AttachmentService Integration Tests** - Test file upload/download with real filesystem | deps: T-002, T-004
- [x] **T-007: VBU API Integration Tests** - Test VBU endpoints with authorization | deps: T-005
- [x] **T-008: Canvas API Integration Tests** - Test canvas endpoints with nested data | deps: T-005
- [x] **T-009: Thesis API Integration Tests** - Test thesis CRUD and reordering | deps: T-005
- [x] **T-010: ProofPoint API Integration Tests** - Test proof point CRUD with attachments | deps: T-006
- [x] **T-011: Attachment API Integration Tests** - Test file upload/download endpoints | deps: T-006
- [x] **T-012: CanvasService Implementation** - Implement canvas business logic with authorization | deps: T-005
- [x] **T-013: AttachmentService Implementation** - Implement file handling with validation | deps: T-006
- [x] **T-014: VBU API Routes** - Implement VBU CRUD endpoints | deps: T-007, T-012
- [x] **T-015: Canvas API Routes** - Implement canvas management endpoints | deps: T-008, T-012
- [x] **T-016: Thesis API Routes** - Implement thesis CRUD and reordering endpoints | deps: T-009, T-012
- [x] **T-017: ProofPoint API Routes** - Implement proof point CRUD endpoints | deps: T-010, T-012
- [x] **T-018: Attachment API Routes** - Implement file upload/download endpoints | deps: T-011, T-013
- [x] **T-019: InlineEdit Component** - Create inline editing component with autosave | deps: none
- [x] **T-020: StatusBadge Component** - Create status badge component with dropdown | deps: none
- [x] **T-021: FileUpload Component** - Create file upload component with drag-and-drop | deps: none
- [x] **T-022: VBU Canvas Page** - Create main canvas page with all sections | deps: T-019, T-020, T-021
- [x] **T-023: Canvas API Client** - Create frontend API client for canvas operations | deps: T-015, T-016, T-017, T-018
- [x] **T-024: Canvas Page Integration** - Wire canvas page with API client and state management | deps: T-022, T-023
- [x] **T-025: App Routing Integration** - Modify App.tsx to include canvas page routes | deps: T-024

## Success Criteria
- ⬜ All tests pass
- ⬜ No lint errors
- ⬜ Feature works end-to-end