# Feature 004: Monthly Review

## Overview

The Monthly Review feature provides a guided 4-step wizard that walks GMs through structured monthly review prompts and captures dated review entries with commitments. It creates MonthlyReview and Commitment entities, updates the canvas "currently testing" pointer, and displays review history on the VBU Canvas page. Reviews can have file attachments.

## Requirements

### FR-001: Monthly Review Wizard
**Description:** GM can complete a guided 4-step wizard for monthly reviews
**Acceptance Criteria:**
- Step 1: "What moved since last month (evidence)?" - text area
- Step 2: "What did we learn that changes our beliefs?" - text area  
- Step 3: "What now threatens the next proof point?" - text area
- Step 4: Commitments (1-3) + currently testing selection
- Step indicator shows current step (1/4, 2/4, etc.)
- Previous/Next navigation between steps
- Submit creates MonthlyReview with current date
- Redirects to canvas page after successful submit

### FR-002: Commitments Management
**Description:** GM can add 1-3 commitments in the final wizard step
**Acceptance Criteria:**
- Add commitment button (max 3)
- Remove commitment button
- Commitments are ordered (1, 2, 3)
- Each commitment is required text
- Commitments saved as separate Commitment entities

### FR-003: Currently Testing Selection
**Description:** GM selects what to focus on next in the final wizard step
**Acceptance Criteria:**
- Radio button list of all theses and proof points from the canvas
- Grouped by thesis (thesis option + its proof points indented)
- Selection updates canvas.currently_testing_type and currently_testing_id
- Can select thesis or individual proof point

### FR-004: Review History Display
**Description:** Review history is visible on the VBU Canvas page
**Acceptance Criteria:**
- Section titled "Review History" on canvas page
- Reviews listed chronologically (newest first)
- Each review shows: date, what_moved excerpt (first 100 chars), commitments count
- Click review to expand full details
- Shows all 3 prompts + commitments + currently testing selection

### FR-005: Review File Attachments
**Description:** Reviews can have file attachments
**Acceptance Criteria:**
- File upload component in wizard (any step)
- Uses shared AttachmentService from 002-canvas-management
- Attachments linked to monthly_review_id
- Attachments displayed in review history
- Download/delete functionality for attachments

### FR-006: Access Control
**Description:** Only authorized users can create/view reviews
**Acceptance Criteria:**
- Admin can create reviews for any VBU
- GM can create reviews only for their own VBUs
- Viewer can view all reviews (read-only)
- 403 error for unauthorized access

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
      "what_moved": "text",
      "what_learned": "text", 
      "what_threatens": "text",
      "currently_testing_type": "thesis|proof_point",
      "currently_testing_id": "uuid",
      "created_by": "uuid",
      "created_at": "2026-02-13T14:00:00Z",
      "commitments": [
        {"id": "uuid", "text": "commitment text", "order": 1}
      ],
      "attachments": [
        {"id": "uuid", "filename": "file.pdf", "label": "Evidence"}
      ]
    }
  ],
  "meta": {"total": 5, "timestamp": "2026-02-13T14:00:00Z"}
}
```

### POST /api/canvases/{canvas_id}/reviews
**Purpose:** Create new review (wizard submit)
**Auth:** JWT required
**Authorization:** Admin (all), GM (own VBUs only)
**Request:**
```json
{
  "review_date": "2026-02-13",
  "what_moved": "text",
  "what_learned": "text",
  "what_threatens": "text", 
  "currently_testing_type": "thesis",
  "currently_testing_id": "uuid",
  "commitments": [
    {"text": "commitment 1", "order": 1},
    {"text": "commitment 2", "order": 2}
  ],
  "attachment_ids": ["uuid1", "uuid2"]
}
```
**Response:**
```json
{
  "data": {
    "id": "uuid",
    "canvas_id": "uuid",
    "review_date": "2026-02-13",
    "what_moved": "text",
    "what_learned": "text",
    "what_threatens": "text",
    "currently_testing_type": "thesis",
    "currently_testing_id": "uuid", 
    "created_by": "uuid",
    "created_at": "2026-02-13T14:00:00Z",
    "commitments": [...],
    "attachments": [...]
  },
  "meta": {"timestamp": "2026-02-13T14:00:00Z"}
}
```

### GET /api/reviews/{id}
**Purpose:** Get single review detail
**Auth:** JWT required
**Authorization:** Admin (all), GM (own VBUs), Viewer (all, read-only)
**Response:** Same as single review object from list endpoint

## Data Models

### MonthlyReview
```python
class MonthlyReview(Base, TimestampMixin):
    __tablename__ = "monthly_reviews"
    
    canvas_id = Column(UUID(as_uuid=True), ForeignKey("canvases.id"), nullable=False)
    review_date = Column(Date, nullable=False)
    what_moved = Column(Text, nullable=True)
    what_learned = Column(Text, nullable=True) 
    what_threatens = Column(Text, nullable=True)
    currently_testing_type = Column(Enum("thesis", "proof_point", name="testing_type"), nullable=True)
    currently_testing_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    canvas = relationship("Canvas", back_populates="monthly_reviews")
    commitments = relationship("Commitment", back_populates="monthly_review", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="monthly_review", cascade="all, delete-orphan")
    created_by_user = relationship("User")
```

### Commitment
```python
class Commitment(Base, TimestampMixin):
    __tablename__ = "commitments"
    
    monthly_review_id = Column(UUID(as_uuid=True), ForeignKey("monthly_reviews.id"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, CheckConstraint("order >= 1 AND order <= 3"))
    
    # Relationships
    monthly_review = relationship("MonthlyReview", back_populates="commitments")
```

## Services

### ReviewService
```python
class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_reviews(self, canvas_id: UUID) -> List[MonthlyReview]:
        """List reviews for canvas, ordered by review_date desc"""
        
    async def create_review(self, canvas_id: UUID, review_data: dict, created_by: UUID) -> MonthlyReview:
        """Create review with commitments, update canvas currently_testing"""
        
    async def get_review(self, review_id: UUID) -> MonthlyReview:
        """Get single review with commitments and attachments"""
        
    async def get_canvas_options(self, canvas_id: UUID) -> dict:
        """Get theses and proof points for currently testing selection"""
```

## UI Components

### Monthly Review Wizard
**Route:** `/vbus/:id/review/new`
**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Monthly Review for [VBU Name]                               │
├─────────────────────────────────────────────────────────────┤
│ Step 1 of 4: What moved since last month?                  │
│ ● ○ ○ ○                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ What moved since last month (evidence)?                     │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ [Large text area for response]                          │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [📎 Attach File]                                           │
│                                                             │
│                                    [Cancel] [Next Step →]  │
└─────────────────────────────────────────────────────────────┘
```

**Step 2:**
```
┌─────────────────────────────────────────────────────────────┐
│ Monthly Review for [VBU Name]                               │
├─────────────────────────────────────────────────────────────┤
│ Step 2 of 4: What did we learn?                            │
│ ● ● ○ ○                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ What did we learn that changes our beliefs?                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ [Large text area for response]                          │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                           [← Previous] [Cancel] [Next →]   │
└─────────────────────────────────────────────────────────────┘
```

**Step 3:**
```
┌─────────────────────────────────────────────────────────────┐
│ Monthly Review for [VBU Name]                               │
├─────────────────────────────────────────────────────────────┤
│ Step 3 of 4: What threatens the next proof point?          │
│ ● ● ● ○                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ What now threatens the next proof point?                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ [Large text area for response]                          │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│                           [← Previous] [Cancel] [Next →]   │
└─────────────────────────────────────────────────────────────┘
```

**Step 4:**
```
┌─────────────────────────────────────────────────────────────┐
│ Monthly Review for [VBU Name]                               │
├─────────────────────────────────────────────────────────────┤
│ Step 4 of 4: Commitments & Focus                           │
│ ● ● ● ●                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Commitments (1-3):                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 1. [Text input for commitment 1]                    [×] │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 2. [Text input for commitment 2]                    [×] │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [+ Add Commitment]                                          │
│                                                             │
│ What are we currently testing?                              │
│ ○ Thesis 1: Customer acquisition strategy                  │
│   ○ Proof Point: 50% increase in trial signups            │
│   ○ Proof Point: 30% improvement in conversion             │
│ ○ Thesis 2: Product-market fit validation                  │
│   ○ Proof Point: NPS score above 50                       │
│                                                             │
│                      [← Previous] [Cancel] [Submit Review] │
└─────────────────────────────────────────────────────────────┘
```

### Review History Section
**Location:** VBU Canvas page, below canvas sections
```
┌─────────────────────────────────────────────────────────────┐
│ Review History                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ February 13, 2026                              [▼]     │ │
│ │ What moved: "Significant progress on user onboarding..." │ │
│ │ 3 commitments • 2 attachments                          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ January 15, 2026                               [▶]     │ │
│ │ What moved: "Customer feedback sessions revealed..."     │ │
│ │ 2 commitments • 1 attachment                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Start Monthly Review]                                      │
└─────────────────────────────────────────────────────────────┘
```

**Expanded Review:**
```
┌─────────────────────────────────────────────────────────────┐
│ February 13, 2026                                  [▲]     │
├─────────────────────────────────────────────────────────────┤
│ What moved since last month?                                │
│ Significant progress on user onboarding flow. Completed    │
│ A/B test showing 25% improvement in completion rates.       │
│                                                             │
│ What did we learn?                                          │
│ Users drop off at the payment step, not the signup step.   │
│ Need to focus on trust signals and pricing clarity.        │
│                                                             │
│ What threatens the next proof point?                        │
│ Engineering capacity is constrained by legacy system       │
│ maintenance. May need to deprioritize other features.      │
│                                                             │
│ Commitments:                                                │
│ 1. Complete payment flow redesign by March 1               │
│ 2. Run user interviews on pricing concerns                  │
│ 3. Negotiate engineering resource allocation with CTO      │
│                                                             │
│ Currently Testing: Thesis 1 - Customer acquisition         │
│                                                             │
│ Attachments:                                                │
│ 📄 A-B Test Results.pdf                           [Download] │
│ 📊 User Interview Notes.xlsx                      [Download] │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/vbus/:id/review/new` | ReviewWizard | 4-step review creation wizard |

## Backend Structure

```
backend/canvas/reviews/
├── __init__.py
├── router.py          # FastAPI routes
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
async def list_reviews(canvas_id: UUID, current_user = Depends(get_current_user)):
    # Authorization check for canvas access
    # Return reviews with commitments and attachments

@router.post("/canvases/{canvas_id}/reviews") 
async def create_review(canvas_id: UUID, review_data: ReviewCreateSchema, current_user = Depends(require_role("admin", "gm"))):
    # Authorization check for canvas ownership
    # Create review, commitments, link attachments
    # Update canvas currently_testing fields
    
@router.get("/reviews/{review_id}")
async def get_review(review_id: UUID, current_user = Depends(get_current_user)):
    # Authorization check for canvas access
    # Return single review with full details
```

### Schemas
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from uuid import UUID

class CommitmentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(..., ge=1, le=3)

class ReviewCreateSchema(BaseModel):
    review_date: date
    what_moved: Optional[str] = None
    what_learned: Optional[str] = None  
    what_threatens: Optional[str] = None
    currently_testing_type: Optional[str] = Field(None, regex="^(thesis|proof_point)$")
    currently_testing_id: Optional[UUID] = None
    commitments: List[CommitmentCreate] = Field(..., min_items=1, max_items=3)
    attachment_ids: List[UUID] = Field(default_factory=list)

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
```

## Dependencies

### Internal Dependencies
- **001-auth:** `get_current_user`, `require_role` for authorization
- **002-canvas-management:** `AttachmentService` for file uploads, Canvas model for currently_testing updates

### External Dependencies
None

## Error Handling

| Scenario | HTTP Status | Error Code | Message |
|----------|-------------|------------|---------|
| Canvas not found | 404 | NOT_FOUND | Canvas not found |
| Unauthorized canvas access | 403 | FORBIDDEN | Cannot access this canvas |
| Invalid commitment count | 422 | VALIDATION_ERROR | Must have 1-3 commitments |
| Invalid currently_testing selection | 422 | VALIDATION_ERROR | Selected thesis/proof point not found |
| Review not found | 404 | NOT_FOUND | Review not found |

## Testing Strategy

### Backend Tests
- `test_list_reviews()` - Authorization and data retrieval
- `test_create_review()` - Full wizard flow, commitment creation, canvas update
- `test_create_review_with_attachments()` - File attachment linking
- `test_unauthorized_access()` - GM can only access own VBUs
- `test_invalid_commitments()` - Validation errors
- `test_currently_testing_update()` - Canvas pointer update

### Frontend Tests  
- `ReviewWizard.test.tsx` - Step navigation, form validation, submission
- `ReviewHistory.test.tsx` - Review display, expand/collapse, attachment download

## Security Considerations

- Reviews contain sensitive strategic information - strict authorization required
- File attachments inherit same access controls as reviews
- Currently testing selection must validate thesis/proof point belongs to canvas
- Review creation updates canvas - ensure atomic transaction

## Performance Considerations

- Review history loaded lazily on canvas page
- Attachments loaded on-demand when review expanded
- Index on canvas_id and review_date for chronological listing
- Limit review history display (e.g., last 12 months) for large datasets