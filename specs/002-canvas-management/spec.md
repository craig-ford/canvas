# Feature 002: Canvas Management

## Overview

Canvas Management provides full CRUD operations for VBUs and their Strategy + Lifecycle Canvases, including all nested entities (theses, proof points, file attachments). This feature enables GMs to create and maintain their living strategy documents with inline editing and autosave functionality.

## Dependencies

- **001-auth**: User authentication, role-based access control, JWT validation
- **001A-infrastructure**: Database connection, response helpers, error handling

## Dependents

- **003-portfolio-dashboard**: Reads canvas data for dashboard aggregation
- **004-monthly-review**: Updates canvas "currently testing" pointer

## Functional Requirements

### FR-001: VBU Management
**Description:** Admin users can create, read, update, and delete VBUs. GMs can only read/update their own VBUs.

**Acceptance Criteria:**
- Admin can create VBU with name 1-255 chars and valid GM ID
- Admin can view all VBUs with pagination (25 per page default)
- Admin can update VBU name and reassign GM
- Admin can delete VBU (cascades to canvas and all nested data)
- GM can view only their assigned VBUs
- GM can update name of their own VBUs only
- Viewer can view all VBUs (read-only)
- VBU creation automatically creates associated canvas with lifecycle_lane='build'

### FR-002: Canvas CRUD
**Description:** Each VBU has exactly one canvas containing all strategy sections with inline editing and autosave.

**Acceptance Criteria:**
- Canvas contains all required fields: lifecycle_lane, success_description, future_state_intent, primary_focus, resist_doing, good_discipline, primary_constraint
- Canvas has optional product_name field (1-255 chars when provided)
- Canvas tracks currently_testing pointer (thesis or proof_point) with referential integrity
- Portfolio notes field is admin-only, ignored for non-admin updates
- Canvas updates track updated_by user and timestamp
- Inline editing with 2-second autosave delay and visual feedback
- Concurrent editing uses last-write-wins strategy

### FR-003: Thesis Management
**Description:** Each canvas can have up to 5 theses in a specific order with drag-and-drop reordering.

**Acceptance Criteria:**
- Exactly 5 theses maximum per canvas, 6th returns 422 VALIDATION_ERROR
- Theses are ordered (1-5) with unique constraint per canvas
- Thesis text is required (1+ chars) and supports full-text search
- Theses can be reordered via drag-and-drop with optimistic UI updates
- Deleting thesis cascades to all proof points and attachments
- Order constraint prevents duplicates and gaps

### FR-004: Proof Point Management
**Description:** Each thesis can have multiple proof points with status tracking and evidence notes.

**Acceptance Criteria:**
- Proof points belong to a thesis with cascade delete
- Status must be one of: not_started, in_progress, observed, stalled (default: not_started)
- Description is required (1+ chars) with full-text search capability
- Evidence note is optional with no length limit
- Target review month is optional, accepts future dates
- Proof points can have multiple file attachments
- Status changes trigger dashboard health aggregation updates

### FR-005: File Attachment System
**Description:** Files can be attached to proof points with comprehensive validation and security.

**Acceptance Criteria:**
- Maximum file size: 10MB per file, enforced on frontend and backend
- Allowed types: image/png, image/jpeg, image/gif, application/pdf, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Files stored at `/uploads/{vbu_id}/proof_point/{uuid}.{ext}` with unique paths
- Original filename preserved in database with optional user label
- Files can be downloaded by authorized users with proper MIME headers
- Files can be deleted by authorized users with cleanup from filesystem
- Upload progress indication and error handling for large files
- Virus scanning and content validation (future enhancement)

### FR-006: Currently Testing Pointer
**Description:** Canvas tracks which thesis or proof point is currently being tested with visual indicators.

**Acceptance Criteria:**
- Currently testing can point to thesis OR proof point (polymorphic)
- Referential integrity enforced - invalid IDs return 422 VALIDATION_ERROR
- Can be null (nothing currently being tested)
- Updated during monthly review process and manual selection
- Displayed on portfolio dashboard with star indicators
- Searchable dropdown with thesis/proof point descriptions

### FR-007: Inline Editing with Autosave
**Description:** Canvas sections support inline editing with automatic saving and user feedback.

**Acceptance Criteria:**
- Text fields become editable on click/focus with clear visual state
- Changes are saved automatically after 2 second idle delay
- Visual feedback shows save status (saving/saved/error) with icons
- No explicit save button required for basic editing
- ESC key cancels edit, Enter saves single-line fields
- Concurrent editing protection (last write wins) with conflict indication
- Network error handling with retry options and offline indicators

### FR-008: Authorization
**Description:** Comprehensive role-based access control with data scoping.

**Acceptance Criteria:**
- Admin: Full access to all VBUs, canvases, and portfolio notes
- GM: Full access to own VBUs only, cannot access other GMs' data
- Viewer: Read-only access to all VBUs and canvases
- File uploads restricted to Admin/GM of owning VBU
- Portfolio notes field restricted to Admin only (field ignored for others)
- Authorization failures return 403 FORBIDDEN with generic messages
- Database queries include ownership filters for GM role
- Audit logging for all authorization failures and sensitive operations

## API Endpoints

### VBU Endpoints

| Method | Path | Auth | Description | Query Params |
|--------|------|------|-------------|--------------|
| GET | /api/vbus | JWT | List VBUs (filtered by role) | page, per_page, gm_id, name |
| POST | /api/vbus | Admin | Create VBU | - |
| GET | /api/vbus/{id} | JWT | Get VBU detail | - |
| PATCH | /api/vbus/{id} | Admin/GM | Update VBU | - |
| DELETE | /api/vbus/{id} | Admin | Delete VBU | - |

### Canvas Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/vbus/{vbu_id}/canvas | JWT | Get canvas for VBU with nested data |
| PUT | /api/vbus/{vbu_id}/canvas | GM/Admin | Create or update canvas |

### Thesis Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/canvases/{canvas_id}/theses | JWT | List theses with proof points |
| POST | /api/canvases/{canvas_id}/theses | GM/Admin | Create thesis |
| PATCH | /api/theses/{id} | GM/Admin | Update thesis text |
| DELETE | /api/theses/{id} | GM/Admin | Delete thesis (cascade) |
| PUT | /api/canvases/{canvas_id}/theses/reorder | GM/Admin | Reorder theses |

### Proof Point Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/theses/{thesis_id}/proof-points | JWT | List proof points with attachments |
| POST | /api/theses/{thesis_id}/proof-points | GM/Admin | Create proof point |
| PATCH | /api/proof-points/{id} | GM/Admin | Update proof point |
| DELETE | /api/proof-points/{id} | GM/Admin | Delete proof point |

### Attachment Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/attachments | GM/Admin | Upload file (multipart/form-data) |
| GET | /api/attachments/{id} | JWT | Download file |
| DELETE | /api/attachments/{id} | GM/Admin | Delete attachment |

### Standard Response Envelopes

**Success Response:**
```json
{
  "data": { ... },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

**List Response:**
```json
{
  "data": [ ... ],
  "meta": { "total": 42, "page": 1, "per_page": 25, "timestamp": "..." }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [ { "field": "email", "message": "Already exists" } ]
  }
}
```

### Standard Error Codes
| Code | HTTP Status | Meaning |
|------|-------------|---------|
| VALIDATION_ERROR | 422 | Request body/params invalid |
| NOT_FOUND | 404 | Resource doesn't exist |
| UNAUTHORIZED | 401 | Missing or invalid JWT |
| FORBIDDEN | 403 | Valid JWT but insufficient role |
| CONFLICT | 409 | Duplicate resource (e.g., thesis order) |
| FILE_TOO_LARGE | 413 | Upload exceeds 10MB |
| UNSUPPORTED_TYPE | 415 | File type not in allowed list |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| INTERNAL_ERROR | 500 | Unexpected server error |

## Data Models

### VBU Model
```python
class VBU(TimestampMixin, Base):
    __tablename__ = "vbus"
    
    name = Column(String(255), nullable=False, CheckConstraint("LENGTH(TRIM(name)) > 0"))
    gm_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    gm = relationship("User", foreign_keys=[gm_id])
    canvas = relationship("Canvas", back_populates="vbu", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_vbus_gm_id", "gm_id"),
        Index("ix_vbus_name_gin", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
        Index("ix_vbus_updated_at", "updated_at", postgresql_using="btree"),
    )
```

### Canvas Model
```python
class Canvas(TimestampMixin, Base):
    __tablename__ = "canvases"
    
    vbu_id = Column(UUID(as_uuid=True), ForeignKey("vbus.id", ondelete="CASCADE"), unique=True, nullable=False)
    product_name = Column(String(255), CheckConstraint("product_name IS NULL OR LENGTH(TRIM(product_name)) > 0"))
    lifecycle_lane = Column(Enum(LifecycleLane), nullable=False, default=LifecycleLane.BUILD)
    success_description = Column(Text)
    future_state_intent = Column(Text)
    primary_focus = Column(String(255))
    resist_doing = Column(Text)
    good_discipline = Column(Text)
    primary_constraint = Column(Text)
    currently_testing_type = Column(Enum(CurrentlyTestingType))
    currently_testing_id = Column(UUID(as_uuid=True))
    portfolio_notes = Column(Text)  # Admin-only field
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    vbu = relationship("VBU", back_populates="canvas")
    theses = relationship("Thesis", back_populates="canvas", cascade="all, delete-orphan", order_by="Thesis.order")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("(currently_testing_type IS NULL) = (currently_testing_id IS NULL)", name="ck_currently_testing_consistency"),
        Index("uq_canvases_vbu_id", "vbu_id", unique=True),
        Index("ix_canvases_lifecycle_lane", "lifecycle_lane"),
        Index("ix_canvases_currently_testing", "currently_testing_type", "currently_testing_id"),
    )
```

### Thesis Model
```python
class Thesis(TimestampMixin, Base):
    __tablename__ = "theses"
    
    canvas_id = Column(UUID(as_uuid=True), ForeignKey("canvases.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, CheckConstraint("order BETWEEN 1 AND 5"), nullable=False)
    text = Column(Text, nullable=False, CheckConstraint("LENGTH(TRIM(text)) > 0"))
    
    # Relationships
    canvas = relationship("Canvas", back_populates="theses")
    proof_points = relationship("ProofPoint", back_populates="thesis", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("canvas_id", "order", name="uq_theses_canvas_order"),
        Index("ix_theses_canvas_id", "canvas_id"),
        Index("ix_theses_text_gin", "text", postgresql_using="gin", postgresql_ops={"text": "gin_trgm_ops"}),
    )
```

### ProofPoint Model
```python
class ProofPoint(TimestampMixin, Base):
    __tablename__ = "proof_points"
    
    thesis_id = Column(UUID(as_uuid=True), ForeignKey("theses.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False, CheckConstraint("LENGTH(TRIM(description)) > 0"))
    status = Column(Enum(ProofPointStatus), nullable=False, default=ProofPointStatus.NOT_STARTED)
    evidence_note = Column(Text)
    target_review_month = Column(Date, CheckConstraint("target_review_month >= CURRENT_DATE - INTERVAL '1 year'"))
    
    # Relationships
    thesis = relationship("Thesis", back_populates="proof_points")
    attachments = relationship("Attachment", back_populates="proof_point", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_proof_points_thesis_id", "thesis_id"),
        Index("ix_proof_points_status", "status"),
        Index("ix_proof_points_target_month", "target_review_month"),
        Index("ix_proof_points_description_gin", "description", postgresql_using="gin", postgresql_ops={"description": "gin_trgm_ops"}),
    )
```

### Attachment Model
```python
class Attachment(TimestampMixin, Base):
    __tablename__ = "attachments"
    
    proof_point_id = Column(UUID(as_uuid=True), ForeignKey("proof_points.id", ondelete="CASCADE"))
    monthly_review_id = Column(UUID(as_uuid=True), ForeignKey("monthly_reviews.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False, CheckConstraint("LENGTH(TRIM(filename)) > 0"))
    storage_path = Column(String(1024), nullable=False, unique=True, CheckConstraint("LENGTH(TRIM(storage_path)) > 0"))
    content_type = Column(String(128), nullable=False, CheckConstraint("content_type IN ('image/png','image/jpeg','image/gif','application/pdf','text/csv','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')"))
    size_bytes = Column(Integer, nullable=False, CheckConstraint("size_bytes BETWEEN 1 AND 10485760"))
    label = Column(String(255), CheckConstraint("label IS NULL OR LENGTH(TRIM(label)) > 0"))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    proof_point = relationship("ProofPoint", back_populates="attachments")
    uploader = relationship("User")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("(proof_point_id IS NOT NULL AND monthly_review_id IS NULL) OR (proof_point_id IS NULL AND monthly_review_id IS NOT NULL)", name="ck_attachment_single_parent"),
        Index("ix_attachments_proof_point_id", "proof_point_id"),
        Index("ix_attachments_monthly_review_id", "monthly_review_id"),
        Index("ix_attachments_uploaded_by", "uploaded_by"),
        Index("ix_attachments_content_type", "content_type"),
        Index("uq_attachments_storage_path", "storage_path", unique=True),
    )
```

## Service Layer

### AttachmentService
**Implements cross-cutting contract from specs/cross-cutting.md**

```python
class AttachmentService:
    def __init__(self, upload_dir: str, max_size_mb: int):
        self.upload_dir = Path(upload_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_types = {
            "image/png", "image/jpeg", "image/gif", 
            "application/pdf", "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    
    async def upload(self, file: UploadFile, vbu_id: UUID, entity_type: str, uploaded_by: UUID) -> Attachment:
        """Upload file with validation and virus scanning"""
        # Validate file size and type
        # Generate UUID-based storage path: /uploads/{vbu_id}/{entity_type}/{uuid}.{ext}
        # Save file to disk atomically
        # Create attachment record in database
        # Return attachment model
        pass
    
    async def download(self, attachment_id: UUID) -> FileResponse:
        """Download file with proper headers and authorization"""
        # Fetch attachment record with authorization check
        # Return FileResponse with correct MIME type and filename
        pass
    
    async def delete(self, attachment_id: UUID) -> None:
        """Delete file from disk and database"""
        # Delete file from filesystem
        # Delete attachment record from database
        # Handle cleanup errors gracefully
        pass
```

### CanvasService
```python
class CanvasService:
    async def get_canvas_by_vbu(self, vbu_id: UUID, db: AsyncSession) -> Canvas:
        """Get canvas with all nested data (theses, proof points, attachments)"""
        pass
    
    async def update_canvas(self, vbu_id: UUID, canvas_data: CanvasUpdate, updated_by: UUID, db: AsyncSession) -> Canvas:
        """Update canvas fields with authorization and audit logging"""
        pass
    
    async def update_currently_testing(self, canvas_id: UUID, testing_type: str, testing_id: UUID, db: AsyncSession) -> Canvas:
        """Update currently testing pointer with referential integrity check"""
        pass
```

## Pydantic Schemas

### Request Schemas
```python
class VBUCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="VBU name")
    gm_id: UUID = Field(..., description="General Manager user ID")

class VBUUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    gm_id: Optional[UUID] = None

class CanvasUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=255)
    lifecycle_lane: Optional[LifecycleLane] = None
    success_description: Optional[str] = None
    future_state_intent: Optional[str] = None
    primary_focus: Optional[str] = Field(None, max_length=255)
    resist_doing: Optional[str] = None
    good_discipline: Optional[str] = None
    primary_constraint: Optional[str] = None
    portfolio_notes: Optional[str] = None  # Admin-only field

class ThesisCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Thesis statement")
    order: int = Field(..., ge=1, le=5, description="Display order 1-5")

class ThesisUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)

class ThesesReorder(BaseModel):
    thesis_orders: List[Dict[str, Union[UUID, int]]] = Field(..., description="List of {id, order} pairs")

class ProofPointCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Observable signal description")
    status: ProofPointStatus = ProofPointStatus.NOT_STARTED
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None

class ProofPointUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[ProofPointStatus] = None
    evidence_note: Optional[str] = None
    target_review_month: Optional[date] = None
```

### Response Schemas
```python
class VBUResponse(BaseModel):
    id: UUID
    name: str
    gm_id: UUID
    gm_name: str
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[UUID]

class AttachmentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size_bytes: int
    label: Optional[str]
    uploaded_by: UUID
    created_at: datetime

class ProofPointResponse(BaseModel):
    id: UUID
    description: str
    status: ProofPointStatus
    evidence_note: Optional[str]
    target_review_month: Optional[date]
    attachments: List[AttachmentResponse]
    created_at: datetime
    updated_at: datetime

class ThesisResponse(BaseModel):
    id: UUID
    order: int
    text: str
    proof_points: List[ProofPointResponse]
    created_at: datetime
    updated_at: datetime

class CanvasResponse(BaseModel):
    id: UUID
    vbu_id: UUID
    product_name: Optional[str]
    lifecycle_lane: LifecycleLane
    success_description: Optional[str]
    future_state_intent: Optional[str]
    primary_focus: Optional[str]
    resist_doing: Optional[str]
    good_discipline: Optional[str]
    primary_constraint: Optional[str]
    currently_testing_type: Optional[CurrentlyTestingType]
    currently_testing_id: Optional[UUID]
    portfolio_notes: Optional[str]  # Only visible to admin users
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[UUID]
```

## UI Components

### VBU Canvas Page Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ [← Dashboard] VBU Name                    [Start Monthly Review] │
├─────────────────────────────────────────────────────────────────┤
│ [Autosave: Saved ✓] [Last updated: 2 min ago by John Doe]      │
├─────────────────────────────────────────────────────────────────┤
│ ┌─ Context Section ─────────────────────────────────────────┐   │
│ │ Product Name: [Click to edit...                    ] [📝] │   │
│ │ Lifecycle: [Build] [Sell] [Milk] [Reframe]               │   │
│ │ Success Description: [Click to edit...             ] [📝] │   │
│ │ Future State Intent: [Click to edit...             ] [📝] │   │
│ └───────────────────────────────────────────────────────────┘   │
│ ┌─ Strategic Focus ──────────────────────────────────────────┐   │
│ │ Primary Focus: [Click to edit...              ] [📝]       │   │
│ │ Resist Doing: [Click to edit...               ] [📝]       │   │
│ │ Good Discipline: [Click to edit...            ] [📝]       │   │
│ │ Primary Constraint: [Click to edit...         ] [📝]       │   │
│ └───────────────────────────────────────────────────────────┘   │
│ ┌─ Strategic Theses (2/5) ──────────────────────────────────┐   │
│ │ 1. [⋮⋮] [Thesis text...] [×] [⭐ Testing]                 │   │
│ │    • [Proof point...] [In Progress ▾] [📎 2] [×] [⭐]     │   │
│ │      Evidence: [Click to edit...] [📝]                    │   │
│ │      Target: [Mar 2026 ▾]                                 │   │
│ │    • [+ Add Proof Point]                                  │   │
│ │ 2. [⋮⋮] [Second thesis...] [×]                            │   │
│ │ [+ Add Thesis (3/5 remaining)]                            │   │
│ └───────────────────────────────────────────────────────────┘   │
│ ┌─ Currently Testing ───────────────────────────────────────┐   │
│ │ Focus: [Thesis 1: "Customer acquisition..." ▾]           │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key UI Components

#### InlineEdit Component
```typescript
interface InlineEditProps {
  value: string;
  onSave: (value: string) => Promise<void>;
  multiline?: boolean;
  placeholder?: string;
  readonly?: boolean;
}

const InlineEdit: React.FC<InlineEditProps> = ({ value, onSave, multiline, placeholder, readonly }) => {
  // Click to edit, auto-save after 2s delay, ESC to cancel, visual feedback
  // Shows saving/saved/error states with icons
  // Handles network errors with retry options
};
```

#### StatusBadge Component
```typescript
interface StatusBadgeProps {
  status: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  onChange?: (status: string) => void;
  readonly?: boolean;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, onChange, readonly }) => {
  // Colored badge with dropdown for status change
  // Colors: not_started=gray, in_progress=teal, observed=green, stalled=yellow
};
```

#### FileUpload Component
```typescript
interface FileUploadProps {
  onUpload: (file: File, label?: string) => Promise<void>;
  attachments: Attachment[];
  onDelete: (id: string) => Promise<void>;
  maxSize: number;
  allowedTypes: string[];
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload, attachments, onDelete, maxSize, allowedTypes }) => {
  // Drag & drop file upload with progress indication
  // File validation and error handling
  // Attachment list with download/delete actions
};
```

## Environment Variables

Uses shared environment variables from cross-cutting.md:
- `CANVAS_UPLOAD_DIR`: File upload directory (default: /uploads)
- `CANVAS_MAX_UPLOAD_SIZE_MB`: Max upload file size (default: 10)

## Security Considerations

### Authentication & Authorization
- All endpoints require valid JWT token in `Authorization: Bearer {token}` header
- Role-based access control with data scoping by VBU ownership
- Portfolio notes field restricted to admin users only
- File access restricted to users with VBU access rights

### Input Validation & Sanitization
- File size validation: 1 byte to 10MB
- MIME type validation against allowed list
- Path traversal prevention in file storage
- HTML escaping for all text inputs
- UUID format validation for all ID parameters

### Data Protection
- File attachments encrypted at rest (filesystem level)
- Sensitive data masked in logs (emails, file paths)
- No sensitive information in error responses
- Audit logging for all authorization failures and file operations

### Rate Limiting
- File upload: 10 requests/minute per user
- Canvas updates: 60 requests/minute per user
- Total API requests: 1000 requests/hour per user
- Progressive backoff for repeated authorization failures

## Error Handling

### Validation Errors
- File too large: HTTP 413, code "FILE_TOO_LARGE"
- Unsupported file type: HTTP 415, code "UNSUPPORTED_TYPE"
- Thesis limit exceeded: HTTP 422, code "VALIDATION_ERROR"
- Invalid order values: HTTP 422, code "VALIDATION_ERROR"

### Authorization Errors
- GM accessing other's VBU: HTTP 403, code "FORBIDDEN"
- Viewer attempting edit: HTTP 403, code "FORBIDDEN"
- Portfolio notes access by non-admin: Field ignored, no error

### Business Logic Errors
- Canvas not found: HTTP 404, code "NOT_FOUND"
- Currently testing invalid ID: HTTP 422, code "VALIDATION_ERROR"
- Duplicate thesis order: HTTP 409, code "CONFLICT"

## Testing Strategy

### Unit Tests
- AttachmentService: File validation, storage path generation, cleanup
- Authorization helpers: Role checking, ownership validation
- Pydantic schemas: Validation rules, field constraints

### Integration Tests
- VBU CRUD endpoints with role-based authorization
- Canvas management with nested data loading
- File upload/download with multipart handling
- Thesis operations: CRUD, reordering, cascade deletes

### Edge Cases
- Concurrent canvas editing (last write wins)
- File upload edge cases (size limits, invalid types)
- Thesis ordering constraints and validation
- Authorization boundary testing across all roles

## Performance Considerations

- Canvas data loaded in single request with nested relationships
- File uploads processed with progress indication
- Autosave debounced to prevent excessive API calls
- Database indexes on foreign keys and frequently queried fields
- Pagination for VBU listings (25 per page default)
```
```