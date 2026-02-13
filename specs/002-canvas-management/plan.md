# specs/002-canvas-management/plan.md

## Overview
Canvas Management provides full CRUD operations for VBUs and their Strategy + Lifecycle Canvases, including nested entities (theses, proof points, file attachments). The feature implements a library-first architecture with CLI exposure, inline editing with autosave, and comprehensive role-based authorization. Core logic resides in importable services with FastAPI providing a thin API veneer.

## Constitutional Gate Review

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | ✓ | Core logic in CanvasService, AttachmentService libraries. FastAPI routes are thin wrappers calling service methods. |
| CLI Mandate | ✓ | Services expose CLI commands: canvas-cli create-vbu, canvas-cli upload-file, etc. JSON stdout, errors to stderr. |
| Test-First | ✓ | Contract tests verify service interfaces before implementation. Integration tests use real database. |
| Integration-First | ✓ | Real PostgreSQL, real file system. No mocks except for external dependencies (none in this feature). |
| Simplicity Gate | ✓ | 5 entities (VBU, Canvas, Thesis, ProofPoint, Attachment), 4 main endpoints. No premature abstraction. |
| Single Domain Model | ✓ | One model per concept. No DTOs except at API serialization boundary (Pydantic schemas). |

## Dependencies

### Cross-Feature (from master-spec.md)
| Feature | What We Import | Status |
|---------|----------------|--------|
| 001-auth | get_current_user, require_role dependencies | Must be complete |
| 001A-infrastructure | success_response, list_response, TimestampMixin, database session | Must be complete |

### External Libraries
| Library | Version | Purpose |
|---------|---------|--------|
| FastAPI | >=0.128.0 | API framework |
| SQLAlchemy | >=2.0 | Async ORM |
| Pydantic | >=2.13.0 | Data validation |
| python-multipart | Latest | File upload handling |
| aiofiles | Latest | Async file operations |

## Implementation Phases

### Phase 1: Contracts & Interfaces
- [ ] Define CanvasService interface with all CRUD methods
- [ ] Define AttachmentService interface (cross-cutting contract)
- [ ] Define Pydantic schemas for all request/response models
- [ ] Define SQLAlchemy models with relationships and constraints
- [ ] Define CLI interface specifications
Estimate: ~200 LOC

### Phase 2: Test Infrastructure  
- [ ] Contract tests for CanvasService interface
- [ ] Contract tests for AttachmentService interface
- [ ] Integration test fixtures (test database, file cleanup)
- [ ] Test factories for all entities
- [ ] Authorization test helpers
Estimate: ~300 LOC

### Phase 3: Data Layer
- [ ] SQLAlchemy models: VBU, Canvas, Thesis, ProofPoint, Attachment
- [ ] Database migrations via Alembic
- [ ] Indexes for performance and constraints
- [ ] Seed data for development
Estimate: ~250 LOC

### Phase 4: Core Logic
- [ ] CanvasService implementation with authorization
- [ ] AttachmentService implementation with file validation
- [ ] Authorization helpers for role-based access
- [ ] Business logic validation and error handling
Estimate: ~400 LOC

### Phase 5: API Layer
- [ ] VBU CRUD endpoints with role filtering
- [ ] Canvas management endpoints
- [ ] Thesis and ProofPoint CRUD endpoints
- [ ] File upload/download endpoints with multipart handling
- [ ] CLI commands wrapping service methods
Estimate: ~350 LOC

### Phase 6: UI
- [ ] VBU Canvas page with all sections
- [ ] InlineEdit component with autosave
- [ ] FileUpload component with drag-and-drop
- [ ] StatusBadge component for proof points
- [ ] Authorization-aware UI state management
Estimate: ~600 LOC

## Parallel Work Opportunities
- Phase 3 (Data Layer) and Phase 2 (Test Infrastructure) can run concurrently
- Phase 4 (Core Logic) can begin once Phase 1 contracts are defined
- Phase 6 (UI) can begin once Phase 5 API endpoints are available
- CLI implementation can run parallel to API implementation in Phase 5

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| File upload complexity | Medium | High | Start with simple local storage, comprehensive validation |
| Authorization edge cases | High | Medium | Extensive test coverage for all role combinations |
| Concurrent editing conflicts | Medium | Medium | Implement last-write-wins with clear user feedback |
| Database constraint violations | Low | High | Comprehensive validation in service layer before DB calls |
| Large file handling | Medium | Medium | Streaming uploads, progress indication, size limits |

## Total Estimate
~2100 LOC across 25 tasks