# specs/002-canvas-management/tasks.md

## Progress
Total: 20 tasks | Complete: 0 | Remaining: 20

## Tasks
- [ ] **T-001: Canvas Service Contract Tests** - Define and test CanvasService interface with all CRUD methods | deps: none
- [ ] **T-002: Attachment Service Contract Tests** - Define and test AttachmentService interface for file operations | deps: none
- [ ] **T-003: SQLAlchemy Models** - Create VBU, Canvas, Thesis, ProofPoint, Attachment models with relationships | deps: none
- [ ] **T-004: Pydantic Schemas** - Define request/response schemas for all entities with validation | deps: T-003
- [ ] **T-005: Database Integration Tests** - Test model relationships, constraints, and cascade operations | deps: T-003
- [ ] **T-006: Authorization Integration Tests** - Test role-based access control across all operations | deps: T-003
- [ ] **T-007: VBU Service Unit Tests** - Test VBU CRUD operations with authorization and validation | deps: T-001, T-003
- [ ] **T-008: Canvas Service Unit Tests** - Test canvas operations, nested data loading, currently testing pointer | deps: T-001, T-003
- [ ] **T-009: Thesis Service Unit Tests** - Test thesis CRUD, ordering constraints, cascade deletes | deps: T-001, T-003
- [ ] **T-010: ProofPoint Service Unit Tests** - Test proof point operations, status tracking, evidence notes | deps: T-001, T-003
- [ ] **T-011: Attachment Service Unit Tests** - Test file upload, validation, storage, and cleanup | deps: T-002, T-003
- [ ] **T-012: CanvasService Implementation** - Implement core canvas management logic with authorization | deps: T-008
- [ ] **T-013: AttachmentService Implementation** - Implement file operations with validation and security | deps: T-011
- [ ] **T-014: VBU API Endpoints** - Implement VBU CRUD routes with role-based filtering | deps: T-007, T-012
- [ ] **T-015: Canvas API Endpoints** - Implement canvas management routes with nested data | deps: T-008, T-012
- [ ] **T-016: Thesis API Endpoints** - Implement thesis CRUD and reordering routes | deps: T-009, T-012
- [ ] **T-017: ProofPoint API Endpoints** - Implement proof point CRUD routes with status management | deps: T-010, T-012
- [ ] **T-018: Attachment API Endpoints** - Implement file upload/download routes with multipart handling | deps: T-011, T-013
- [ ] **T-019: CLI Commands** - Implement CLI interface for all canvas operations | deps: T-012, T-013
- [ ] **T-020: Database Migrations** - Create Alembic migrations for all canvas management tables | deps: T-003

## Success Criteria
- ⬜ All tests pass
- ⬜ No lint errors
- ⬜ Feature works end-to-end
- ⬜ Authorization enforced correctly
- ⬜ File operations secure and validated
- ⬜ CLI commands functional