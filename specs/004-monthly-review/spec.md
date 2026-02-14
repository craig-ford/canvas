# Feature 004: Monthly Review

## Overview

The Monthly Review feature provides a guided 4-step wizard that walks GMs through structured monthly review prompts and captures dated review entries with commitments. It creates MonthlyReview and Commitment entities, updates the canvas "currently testing" pointer, and displays review history on the VBU Canvas page. Reviews can have file attachments.

## Requirements

### FR-001: Monthly Review Wizard
**Description:** GM can complete a guided 4-step wizard for monthly reviews
**Acceptance Criteria:**
- Step 1: "What moved since last month (evidence)?" - text area with 2000 char limit
- Step 2: "What did we learn that changes our beliefs?" - text area with 2000 char limit
- Step 3: "What now threatens the next proof point?" - text area with 2000 char limit
- Step 4: Commitments (1-3) + currently testing selection
- Step indicator displays "Step X of 4" with visual progress (filled/unfilled circles)
- Previous/Next navigation between steps with form validation
- Auto-save draft every 30 seconds
- Submit creates MonthlyReview with review_date = today's date
- Redirects to canvas page after successful submit

### FR-002: Commitments Management
**Description:** GM can add 1-3 commitments in the final wizard step
**Acceptance Criteria:**
- Add commitment button (disabled at 3 commitments)
- Remove commitment button with confirmation
- Commitments saved with order field 1-3, displayed in ascending order
- Each commitment text required (1-1000 chars)
- Submit disabled if no commitments

### FR-003: Currently Testing Selection
**Description:** GM selects what to focus on next in the final wizard step
**Acceptance Criteria:**
- Hierarchical radio list: thesis as parent, proof points as indented children
- Selection required for submit
- Updates canvas.currently_testing_type and currently_testing_id atomically
- Validation ensures selected item belongs to canvas

### FR-004: Review History Display
**Description:** Review history is visible on the VBU Canvas page
**Acceptance Criteria:**
- Section titled "Review History" on canvas page
- Reviews ordered by review_date DESC, then created_at DESC
- Each review shows: date, what_moved excerpt (100 chars), commitments/attachments count
- Toggle between collapsed (excerpt) and expanded (full text) views
- Shows all 3 prompts + commitments + currently testing selection + attachments

### FR-005: Review File Attachments
**Description:** Reviews can have file attachments
**Acceptance Criteria:**
- Drag/drop file upload in wizard with progress indicator
- Uses shared AttachmentService from 002-canvas-management
- Attachments linked to monthly_review_id
- Supported types: PDF, DOC, XLS, PNG, JPG (max 10MB each)
- Download links in review history

### FR-006: Access Control
**Description:** Only authorized users can create/view reviews
**Acceptance Criteria:**
- Admin: full access to all VBUs
- GM: create/read reviews only for own VBUs (vbu.gm_id == current_user.id)
- Viewer: read-only access to all reviews
- 403 error for unauthorized access with generic "Access denied" message

## API Endpoints

### GET /api/canvases/{canvas_id}/reviews
**Purpose:** List reviews for a canvas
**Auth:** JWT required
**Authorization:** Admin (all), GM (own VBUs), Viewer (all, read-only)
**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "canvas_id": "uuid", 
      "review_date": "2026-02-13",
      "what_moved": "text (max 5000 chars)",
      "what_learned": "text (max 5000 chars)", 
      "what_threatens": "text (max 5000 chars)",
      "currently_testing_type": "thesis|proof_point",
      "currently_testing_id": "uuid",
      "created_by": "uuid",
      "created_at": "2026-02-13T14:00:00Z",
      "commitments": [
        {"id": "uuid", "text": "commitment text (max 1000 chars)", "order": 1}
      ],
      "attachments": [
        {"id": "uuid", "filename": "file.pdf", "label": "Evidence", "size_bytes": 2048576}
      ]
    }
  ],
  "meta": {"total": 5, "timestamp": "2026-02-13T14:00:00Z"}
}
```

**Errors:**
- 401 UNAUTHORIZED: Missing/invalid JWT
- 403 FORBIDDEN: GM accessing other's VBU  
- 404 NOT_FOUND: Canvas not found

### POST /api/canvases/{canvas_id}/reviews
**Purpose:** Create new review (wizard submit)
**Auth:** JWT required
**Authorization:** Admin (all), GM (own VBUs only)
**Request:**
```json
{
  "review_date": "2026-02-13",
  "what_moved": "text (optional, max 5000 chars)",
  "what_learned": "text (optional, max 5000 chars)",
  "what_threatens": "text (optional, max 5000 chars)", 
  "currently_testing_type": "thesis|proof_point (required)",
  "currently_testing_id": "uuid (required)",
  "commitments": [
    {"text": "commitment 1 (1-1000 chars)", "order": 1},
    {"text": "commitment 2 (1-1000 chars)", "order": 2}
  ],
  "attachment_ids": ["uuid1", "uuid2"]
}
```

**Validation:**
- review_date: Required, valid ISO date, not future
- commitments: 1-3 items, unique orders 1-3
- currently_testing_id: Must exist in canvas theses/proof_points
- attachment_ids: Must exist and be unlinked

**Errors:**
- 422 VALIDATION_ERROR: Invalid commitment count/order, text too long
- 422 VALIDATION_ERROR: Invalid currently_testing selection
- 409 CONFLICT: Review already exists for date

### GET /api/reviews/{id}
**Purpose:** Get single review detail
**Auth:** JWT required
**Authorization:** Admin (all), GM (own VBUs), Viewer (all, read-only)
**Response:** Same as single review object from list endpoint

## Data Models

### MonthlyReview
**Table:** monthly_reviews

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| canvas_id | UUID | FK → canvases.id ON DELETE CASCADE, NOT NULL | Parent canvas |
| review_date | DATE | NOT NULL | Review date |
| what_moved | TEXT | NULLABLE | What moved since last month |
| what_learned | TEXT | NULLABLE | What did we learn |
| what_threatens | TEXT | NULLABLE | What now threatens |
| currently_testing_type | ENUM('thesis','proof_point') | NULLABLE | What was selected as focus |
| currently_testing_id | UUID | NULLABLE | Polymorphic FK |
| created_by | UUID | FK → users.id ON DELETE RESTRICT, NOT NULL | Review author |
| created_at | TIMESTAMPTZ | NOT NULL, server default now() | Creation timestamp |

**Constraints:** UNIQUE(canvas_id, review_date)
**Relationships:** belongs_to Canvas via canvas_id; has_many Commitment (max 3, ordered); has_many Attachment
**Indexes:** ix_monthly_reviews_canvas_id on canvas_id; ix_monthly_reviews_review_date on review_date

### Commitment
**Table:** commitments

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Primary key |
| monthly_review_id | UUID | FK → monthly_reviews.id ON DELETE CASCADE, NOT NULL | Parent review |
| text | TEXT | NOT NULL, CHECK(length(text) BETWEEN 1 AND 1000) | Commitment text |
| order | INTEGER | NOT NULL, CHECK(order BETWEEN 1 AND 3) | Display order |

**Constraints:** UNIQUE(monthly_review_id, order)
**Relationships:** belongs_to MonthlyReview via monthly_review_id
**Indexes:** ix_commitments_review_id on monthly_review_id

### Canvas Update Trigger
```sql
CREATE OR REPLACE FUNCTION update_canvas_currently_testing()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.currently_testing_type IS NOT NULL AND NEW.currently_testing_id IS NOT NULL THEN
        UPDATE canvases 
        SET currently_testing_type = NEW.currently_testing_type,
            currently_testing_id = NEW.currently_testing_id,
            updated_at = NOW()
        WHERE id = NEW.canvas_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_canvas_currently_testing
    AFTER INSERT ON monthly_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_canvas_currently_testing();
```

## Services

### ReviewService
```python
class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_reviews(self, canvas_id: UUID) -> List[MonthlyReview]:
        """List reviews for canvas, ordered by review_date DESC, created_at DESC"""
        result = await self.db.execute(
            select(MonthlyReview)
            .where(MonthlyReview.canvas_id == canvas_id)
            .order_by(MonthlyReview.review_date.desc(), MonthlyReview.created_at.desc())
            .options(selectinload(MonthlyReview.commitments), selectinload(MonthlyReview.attachments))
        )
        return result.scalars().all()
    
    async def create_review(self, canvas_id: UUID, review_data: dict, created_by: UUID) -> MonthlyReview:
        """Create review with commitments, update canvas currently_testing atomically"""
        async with self.db.begin():
            # Validate currently_testing selection belongs to canvas
            await self._validate_currently_testing(canvas_id, review_data.get('currently_testing_type'), 
                                                 review_data.get('currently_testing_id'))
            
            # Create review
            review = MonthlyReview(
                canvas_id=canvas_id,
                review_date=review_data['review_date'],
                what_moved=review_data.get('what_moved'),
                what_learned=review_data.get('what_learned'),
                what_threatens=review_data.get('what_threatens'),
                currently_testing_type=review_data.get('currently_testing_type'),
                currently_testing_id=review_data.get('currently_testing_id'),
                created_by=created_by
            )
            self.db.add(review)
            await self.db.flush()
            
            # Create commitments
            for commitment_data in review_data['commitments']:
                commitment = Commitment(
                    monthly_review_id=review.id,
                    text=commitment_data['text'],
                    order=commitment_data['order']
                )
                self.db.add(commitment)
            
            # Link attachments
            if review_data.get('attachment_ids'):
                await self._link_attachments(review.id, review_data['attachment_ids'])
            
            await self.db.commit()
            return review
        
    async def get_review(self, review_id: UUID) -> MonthlyReview:
        """Get single review with commitments and attachments"""
        result = await self.db.execute(
            select(MonthlyReview)
            .where(MonthlyReview.id == review_id)
            .options(selectinload(MonthlyReview.commitments), selectinload(MonthlyReview.attachments))
        )
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(404, "Review not found")
        return review
        
    async def get_canvas_options(self, canvas_id: UUID) -> dict:
        """Get theses and proof points for currently testing selection"""
        # Implementation returns hierarchical structure for UI
        pass
    
    async def _validate_currently_testing(self, canvas_id: UUID, testing_type: str, testing_id: UUID):
        """Validate selected thesis/proof point belongs to canvas"""
        if not testing_type or not testing_id:
            return
            
        if testing_type == "thesis":
            result = await self.db.execute(
                select(Thesis).where(Thesis.id == testing_id, Thesis.canvas_id == canvas_id)
            )
        else:  # proof_point
            result = await self.db.execute(
                select(ProofPoint)
                .join(Thesis)
                .where(ProofPoint.id == testing_id, Thesis.canvas_id == canvas_id)
            )
        
        if not result.scalar_one_or_none():
            raise HTTPException(422, "Selected thesis/proof point not found in canvas")
    
    async def _link_attachments(self, review_id: UUID, attachment_ids: List[UUID]):
        """Link pre-uploaded attachments to review"""
        await self.db.execute(
            update(Attachment)
            .where(Attachment.id.in_(attachment_ids))
            .values(monthly_review_id=review_id)
        )
```

## UI Components

### Monthly Review Wizard
**Route:** `/vbus/:id/review/new`

**Step 1: What Moved**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Canvas                    Monthly Review for [VBU Name]               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Step 1 of 4: What moved since last month?                                      │
│ ●━━━○━━━○━━━○                                                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ What moved since last month (evidence)?                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ Focus on measurable outcomes, customer feedback, and concrete progress...  │ │
│ │ ┌─────────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ [Large textarea - 6 rows, 2000 char limit]                             │ │ │
│ │ └─────────────────────────────────────────────────────────────────────────┘ │ │
│ │ 0/2000 characters                                                           │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ Attachments (optional)                                                         │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ 📎 Drag files here or [Browse Files]                                       │ │
│ │ Supported: PDF, DOC, XLS, PNG, JPG (max 10MB each)                        │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ [Save Draft]                                    [Cancel] [Next Step →]        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Step 4: Commitments & Focus**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Step 4 of 4: Commitments & Focus                                               │
│ ○━━━○━━━○━━━●                                                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Commitments (1-3 required)                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ 1. ┌───────────────────────────────────────────────────────────────────┐ [×]│ │
│ │    │ Complete payment flow redesign by March 1                        │    │ │
│ │    └───────────────────────────────────────────────────────────────────┘    │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│ [+ Add Commitment (2 remaining)]                                               │
│                                                                                 │
│ What are we currently testing? (required)                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ ● Thesis 1: Customer acquisition strategy                                  │ │
│ │   ○ Proof Point: 50% increase in trial signups                            │ │
│ │   ○ Proof Point: 30% improvement in conversion                             │ │
│ │ ○ Thesis 2: Product-market fit validation                                  │ │
│ │   ○ Proof Point: NPS score above 50                                       │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ [Save Draft]                           [← Previous] [Cancel] [Submit Review]   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Review History Section
**Location:** VBU Canvas page, below canvas sections
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Review History                                                  [Start Review]  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ 📅 February 13, 2026                                              [▼]     │ │
│ │ What moved: "Significant progress on user onboarding flow..."              │ │
│ │ 💼 3 commitments • 📎 2 attachments • 🎯 Testing: Customer acquisition     │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ 📅 January 15, 2026                                               [▶]     │ │
│ │ What moved: "Customer feedback sessions revealed key insights..."           │ │
│ │ 💼 2 commitments • 📎 1 attachment • 🎯 Testing: Product-market fit        │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Expanded Review Detail**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📅 February 13, 2026                                              [▲]         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 📝 What moved: Significant progress on user onboarding flow. Completed A/B     │
│ test showing 25% improvement in completion rates...                             │
│                                                                                 │
│ 🧠 What learned: Users drop off at payment step, not signup step...            │
│                                                                                 │
│ ⚠️ What threatens: Engineering capacity constrained by legacy maintenance...    │
│                                                                                 │
│ 💼 Commitments:                                                                │
│ 1. Complete payment flow redesign by March 1                                   │
│ 2. Run user interviews on pricing concerns                                      │
│                                                                                 │
│ 🎯 Currently Testing: Thesis 1 - Customer acquisition strategy                 │
│                                                                                 │
│ 📎 Attachments:                                                                │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ 📄 A-B Test Results.pdf (2.3 MB)                              [Download]   │ │
│ │ 📊 User Interview Notes.xlsx (1.1 MB)                         [Download]   │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Interactions
- **Auto-save**: Draft saved every 30 seconds, "Saving..." indicator
- **Validation**: Real-time character counting, error states with red borders
- **File Upload**: Drag/drop with progress bar, file type validation
- **Navigation**: Previous/Next with unsaved changes warning modal
- **Accessibility**: Keyboard navigation, screen reader support, ARIA labels

## Backend Structure

```
backend/canvas/reviews/
├── __init__.py
├── router.py          # FastAPI routes with authorization
├── service.py         # ReviewService business logic  
└── schemas.py         # Pydantic request/response models
```

### Router
```python
from fastapi import APIRouter, Depends, HTTPException
from canvas.auth.dependencies import get_current_user, require_role
from canvas.attachments.service import AttachmentService

router = APIRouter(prefix="/api", tags=["reviews"])

@router.get("/canvases/{canvas_id}/reviews")
async def list_reviews(
    canvas_id: UUID, 
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify canvas access (GM: own VBUs only, Admin/Viewer: all)
    await verify_canvas_access(canvas_id, current_user, db)
    service = ReviewService(db)
    reviews = await service.list_reviews(canvas_id)
    return success_response(reviews)

@router.post("/canvases/{canvas_id}/reviews") 
async def create_review(
    canvas_id: UUID, 
    review_data: ReviewCreateSchema, 
    current_user = Depends(require_role("admin", "gm")),
    db: AsyncSession = Depends(get_db)
):
    # Verify canvas ownership for GMs
    await verify_canvas_access(canvas_id, current_user, db)
    service = ReviewService(db)
    review = await service.create_review(canvas_id, review_data.dict(), current_user.id)
    return success_response(review, 201)
```

### Schemas
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

class CommitmentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(..., ge=1, le=3)

class ReviewCreateSchema(BaseModel):
    review_date: date
    what_moved: Optional[str] = Field(None, max_length=5000)
    what_learned: Optional[str] = Field(None, max_length=5000)
    what_threatens: Optional[str] = Field(None, max_length=5000)
    currently_testing_type: str = Field(..., regex="^(thesis|proof_point)$")
    currently_testing_id: UUID
    commitments: List[CommitmentCreate] = Field(..., min_items=1, max_items=3)
    attachment_ids: List[UUID] = Field(default_factory=list, max_items=10)
    
    @validator('review_date')
    def review_date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Review date cannot be in the future')
        return v
    
    @validator('commitments')
    def unique_commitment_orders(cls, v):
        orders = [c.order for c in v]
        if len(orders) != len(set(orders)):
            raise ValueError('Commitment orders must be unique')
        return v

class CommitmentResponse(BaseModel):
    id: UUID
    text: str
    order: int

class AttachmentResponse(BaseModel):
    id: UUID
    filename: str
    label: Optional[str]
    size_bytes: int

class ReviewResponse(BaseModel):
    id: UUID
    canvas_id: UUID
    review_date: date
    what_moved: Optional[str]
    what_learned: Optional[str]
    what_threatens: Optional[str] 
    currently_testing_type: Optional[str]
    currently_testing_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    commitments: List[CommitmentResponse]
    attachments: List[AttachmentResponse]
    
    class Config:
        from_attributes = True
```

## Dependencies

### Internal Dependencies
- **001-auth:** `get_current_user`, `require_role` for authorization (EXACT signatures from cross-cutting.md)
- **002-canvas-management:** `AttachmentService` for file uploads (EXACT interface from cross-cutting.md)
- **001A-infrastructure:** `success_response`, `list_response` helpers (EXACT signatures from cross-cutting.md)

### External Dependencies
None

## Error Handling

| Scenario | HTTP Status | Error Code | Message | Security Notes |
|----------|-------------|------------|---------|----------------|
| Canvas not found | 404 | NOT_FOUND | Resource not found | Generic message, don't expose existence |
| Unauthorized canvas access | 403 | FORBIDDEN | Access denied | Don't specify reason |
| Invalid commitment count | 422 | VALIDATION_ERROR | Must have 1-3 commitments | Field-level validation only |
| Invalid currently_testing | 422 | VALIDATION_ERROR | Selected item not found | Don't expose internal IDs |
| Review not found | 404 | NOT_FOUND | Resource not found | Generic message |
| Text field too long | 422 | VALIDATION_ERROR | Field exceeds maximum length | Don't expose content |
| Future review date | 422 | VALIDATION_ERROR | Review date cannot be in the future | Business rule violation |
| Duplicate review date | 409 | CONFLICT | Review already exists for this date | Prevent duplicate reviews |
| File upload error | 413/415 | FILE_TOO_LARGE/UNSUPPORTED_TYPE | File validation failed | From AttachmentService |

**Security Considerations:**
- Error messages exclude sensitive data (review content, internal IDs)
- Logs capture metadata only (user_id, canvas_id, action, timestamp)
- Generic 403/404 responses prevent information disclosure
- Rate limiting: 5 review creations/hour per user

## Testing Strategy

### Backend Tests
- `test_create_review_atomic()` - Review, commitments, canvas update in single transaction
- `test_authorization_matrix()` - Admin/GM/Viewer access patterns
- `test_validation_errors()` - Commitment count, text length, date validation
- `test_currently_testing_validation()` - Selection belongs to canvas
- `test_attachment_linking()` - File attachment lifecycle

### Frontend Tests  
- `ReviewWizard.test.tsx` - Step navigation, auto-save, form validation
- `ReviewHistory.test.tsx` - Expand/collapse, attachment download
- `AccessibilityTest.tsx` - Keyboard navigation, screen reader support

### Edge Cases
- Canvas with no theses/proof points → Empty selection list, warning message
- Network failure during submit → Error message, retry option, data preserved
- Concurrent review creation → 409 conflict, load existing review
- File upload interruption → Graceful failure, retry option

## Security Considerations

**Authentication & Authorization:**
- All endpoints require valid JWT token
- GM users restricted to own VBUs via `vbu.gm_id == current_user.id`
- Admin users bypass VBU ownership checks
- Viewer users have read-only access

**Data Protection:**
- Review content may contain strategic information - strict access controls
- Attachment access inherits review permissions
- Database encryption at rest, TLS in transit
- File paths use UUIDs to prevent enumeration

**Audit Logging:**
```json
{
  "timestamp": "2026-02-13T14:00:00Z",
  "event": "review_created",
  "user_id": "uuid",
  "canvas_id": "uuid", 
  "review_id": "uuid",
  "request_id": "uuid"
}
```

## Performance Considerations

- Review history loaded on canvas page load (no pagination for v1)
- Attachments loaded on-demand when review expanded
- Database indexes on canvas_id and review_date for chronological listing
- Auto-save throttled to 30-second intervals
- File uploads limited to 10MB per file, 10 files per review