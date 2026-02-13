# specs/004-monthly-review/tasks.md

## Progress
Total: 18 tasks | Complete: 0 | Remaining: 18

## Tasks
- [ ] **T-001: MonthlyReview Model Contract** - Define MonthlyReview SQLAlchemy model with relationships and constraints | deps: none
- [ ] **T-002: Commitment Model Contract** - Define Commitment SQLAlchemy model with validation constraints | deps: T-001
- [ ] **T-003: ReviewService Interface Contract** - Define ReviewService async methods and signatures | deps: T-001, T-002
- [ ] **T-004: Pydantic Schemas Contract** - Define request/response schemas with validation rules | deps: T-001, T-002
- [ ] **T-005: Database Migration Contract** - Create Alembic migration for monthly_reviews and commitments tables | deps: T-001, T-002
- [ ] **T-006: Canvas Update Trigger Contract** - PostgreSQL trigger to update canvas currently_testing atomically | deps: T-001, T-005
- [ ] **T-007: ReviewService Integration Tests** - Test ReviewService methods with real PostgreSQL and AttachmentService | deps: T-003, T-005, T-006
- [ ] **T-008: Authorization Integration Tests** - Test admin/GM/viewer access patterns for review endpoints | deps: T-003, T-007
- [ ] **T-009: Validation Integration Tests** - Test business rules, constraints, and error handling | deps: T-004, T-007
- [ ] **T-010: ReviewService Unit Tests** - Test individual service methods with focused scenarios | deps: T-007
- [ ] **T-011: Model Unit Tests** - Test MonthlyReview and Commitment model validation and relationships | deps: T-001, T-002
- [ ] **T-012: Schema Unit Tests** - Test Pydantic validation rules and serialization | deps: T-004
- [ ] **T-013: ReviewService Implementation** - Implement ReviewService with atomic transactions and validation | deps: T-010
- [ ] **T-014: FastAPI Routes Implementation** - Implement review endpoints with authorization dependencies | deps: T-013
- [ ] **T-015: ReviewWizard Component** - React component for 4-step review creation wizard | deps: T-014
- [ ] **T-016: ReviewHistory Component** - React component for displaying review history on canvas page | deps: T-014
- [ ] **T-017: Auto-save and File Upload** - Implement draft saving and attachment integration | deps: T-015
- [ ] **T-018: End-to-End Integration** - Complete review workflow from wizard to history display | deps: T-015, T-016, T-017

## Success Criteria
- ⬜ All tests pass
- ⬜ No lint errors
- ⬜ Feature works end-to-end
- ⬜ Review creation updates canvas currently_testing atomically
- ⬜ Authorization enforced (GM own VBUs only, Admin all, Viewer read-only)
- ⬜ File attachments work via AttachmentService integration