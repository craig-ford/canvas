# specs/004-monthly-review/plan.md

## Overview
Building a guided 4-step monthly review wizard that captures structured evidence-based reviews with commitments and file attachments. Creates MonthlyReview and Commitment entities, updates canvas "currently testing" pointer atomically, and displays review history on the VBU Canvas page. Uses shared AttachmentService from 002-canvas-management for file handling.

## Constitutional Gate Review

| Gate | Status | Notes |
|------|--------|-------|
| Library-First | ✓ | ReviewService as standalone library, UI calls service methods |
| CLI Mandate | ✓ | ReviewService exposes CLI with JSON stdout for review operations |
| Test-First | ✓ | Contract tests define service interfaces before implementation |
| Integration-First | ✓ | Real PostgreSQL, real AttachmentService, no mocks |
| Simplicity Gate | ✓ | 2 entities (MonthlyReview, Commitment), 3 endpoints, minimal scope |
| Single Domain Model | ✓ | MonthlyReview/Commitment domain models, no DTOs except API boundary |

## Dependencies

### Cross-Feature (from master-spec.md)
| Feature | What We Import | Status |
|---------|----------------|--------|
| 001-auth | get_current_user, require_role | Complete |
| 002-canvas-management | AttachmentService, Canvas/Thesis/ProofPoint models | Complete |
| 001A-infrastructure | success_response, list_response, TimestampMixin | Complete |

### External Libraries
| Library | Version | Purpose |
|---------|---------|--------|
| FastAPI | >=0.128.0 | API routes and validation |
| SQLAlchemy | >=2.0 | Async ORM with PostgreSQL |
| Pydantic | >=2.13.0 | Request/response validation |
| pytest | Latest | Testing framework |

## Implementation Phases

### Phase 1: Contracts & Interfaces
- [ ] MonthlyReview and Commitment SQLAlchemy models with relationships
- [ ] ReviewService interface with async methods (list_reviews, create_review, get_review)
- [ ] Pydantic schemas for request/response validation
- [ ] Database trigger for canvas currently_testing update
Estimate: ~150 LOC

### Phase 2: Test Infrastructure  
- [ ] Contract tests for ReviewService methods
- [ ] Integration test setup with real PostgreSQL
- [ ] Test fixtures for MonthlyReview/Commitment creation
- [ ] Authorization test cases (admin/gm/viewer access patterns)
Estimate: ~200 LOC

### Phase 3: Data Layer
- [ ] Alembic migration for monthly_reviews and commitments tables
- [ ] Database indexes for performance (canvas_id, review_date)
- [ ] Unique constraint on (canvas_id, review_date)
- [ ] PostgreSQL trigger function for canvas updates
Estimate: ~100 LOC

### Phase 4: Core Logic
- [ ] ReviewService implementation with atomic transactions
- [ ] Currently testing validation (thesis/proof_point belongs to canvas)
- [ ] Attachment linking logic using AttachmentService
- [ ] Business rule validation (1-3 commitments, date constraints)
Estimate: ~250 LOC

### Phase 5: API Layer
- [ ] FastAPI routes with authorization dependencies
- [ ] GET /api/canvases/{canvas_id}/reviews (list with pagination)
- [ ] POST /api/canvases/{canvas_id}/reviews (create with validation)
- [ ] GET /api/reviews/{id} (single review detail)
Estimate: ~150 LOC

### Phase 6: UI
- [ ] ReviewWizard component with 4-step navigation
- [ ] Step components (WhatMoved, WhatLearned, WhatThreatens, CommitmentsAndFocus)
- [ ] ReviewHistory component for canvas page integration
- [ ] Auto-save functionality and file upload integration
Estimate: ~400 LOC

## Parallel Work Opportunities
- Phase 1 and Phase 2 can run concurrently (contracts and tests)
- Phase 4 and Phase 5 can overlap (service and API development)
- Phase 6 UI work can start once Phase 1 contracts are defined

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AttachmentService interface changes | Low | Medium | Use exact interface from cross-cutting.md |
| Canvas update atomicity issues | Medium | High | Use database triggers + transaction boundaries |
| Complex authorization logic | Low | Medium | Reuse existing patterns from 002-canvas-management |
| File upload UX complexity | Medium | Medium | Leverage existing AttachmentService patterns |

## Total Estimate
~1250 LOC across 18 tasks