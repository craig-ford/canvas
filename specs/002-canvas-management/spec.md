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
- Admin can create new VBU with name and assign GM
- Admin can view all VBUs
- Admin can update VBU name and reassign GM
- Admin can delete VBU (cascades to canvas)
- GM can view only their assigned VBUs
- GM can update name of their own VBUs
- Viewer can view all VBUs (read-only)

### FR-002: Canvas CRUD
**Description:** Each VBU has exactly one canvas containing all strategy sections.

**Acceptance Criteria:**
- Canvas is automatically created when VBU is created
- Canvas contains all required fields: lifecycle_lane, success_description, future_state_intent, primary_focus, resist_doing, good_discipline, primary_constraint
- Canvas has optional product_name field
- Canvas tracks currently_testing pointer (thesis or proof_point)
- Portfolio notes field is admin-only
- Canvas updates track updated_by user

### FR-003: Thesis Management
**Description:** Each canvas can have up to 5 theses in a specific order.

**Acceptance Criteria:**
- Maximum 5 theses per canvas
- Theses are ordered (1-5)
- Theses can be reordered
- Thesis text is required
- Deleting thesis cascades to proof points
- Order constraint prevents duplicates

### FR-004: Proof Point Management
**Description:** Each thesis can have multiple proof points with status tracking.

**Acceptance Criteria:**
- Proof points belong to a thesis
- Status must be one of: not_started, in_progress, observed, stalled
- Default status is not_started
- Evidence note is optional
- Target review month is optional
- Proof points can have file attachments

### FR-005: File Attachment System
**Description:** Files can be attached to proof points with size and type restrictions.

**Acceptance Criteria:**
- Maximum file size: 10MB
- Allowed types: image/png, image/jpeg, image/gif, application/pdf, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Files stored at `/uploads/{vbu_id}/proof_point/{uuid}.{ext}`
- Original filename preserved in database
- User-provided label is optional
- Files can be downloaded by authorized users
- Files can be deleted by authorized users

### FR-006: Currently Testing Pointer
**Description:** Canvas tracks which thesis or proof point is currently being tested.

**Acceptance Criteria:**
- Currently testing can point to thesis OR proof point
- Polymorphic relationship using type discriminator
- Can be null (nothing currently being tested)
- Updated during monthly review process
- Displayed on portfolio dashboard

### FR-007: Inline Editing with Autosave
**Description:** Canvas sections support inline editing with automatic saving.

**Acceptance Criteria:**
- Text fields become editable on click/focus
- Changes are saved automatically after 2 second delay
- Visual feedback shows save status (saving/saved/error)
- No explicit save button required
- Concurrent editing protection (last write wins)

### FR-008: Authorization
**Description:** Access control based on user roles and VBU ownership.

**Acceptance Criteria:**
- Admin: Full access to all VBUs and canvases
- GM: Full access to own VBUs only
- Viewer: Read-only access to all VBUs and canvases
- File uploads restricted to Admin/GM of owning VBU
- Portfolio notes field restricted to Admin only

## API Endpoints

### VBU Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/vbus | JWT | List VBUs (filtered by role) |
| POST | /api/vbus | Admin | Create VBU |
| GET | /api/vbus/{id} | JWT | Get VBU detail |
| PATCH | /api/vbus/{id} | Admin/GM | Update VBU |
| DELETE | /api/vbus/{id} | Admin | Delete VBU |

### Canvas Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/vbus/{vbu_id}/canvas | JWT | Get canvas for VBU |
| PUT | /api/vbus/{vbu_id}/canvas | GM/Admin | Create or update canvas |

### Thesis Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/canvases/{canvas_id}/theses | JWT | List theses |
| POST | /api/canvases/{canvas_id}/theses | GM/Admin | Create thesis |
| PATCH | /api/theses/{id} | GM/Admin | Update thesis |
| DELETE | /api/theses/{id} | GM/Admin | Delete thesis |
| PUT | /api/canvases/{canvas_id}/theses/reorder | GM/Admin | Reorder theses |

### Proof Point Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/theses/{thesis_id}/proof-points | JWT | List proof points |
| POST | /api/theses/{thesis_id}/proof-points | GM/Admin | Create proof point |
| PATCH | /api/proof-points/{id} | GM/Admin | Update proof point |
| DELETE | /api/proof-points/{id} | GM/Admin | Delete proof point |

### Attachment Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/attachments | GM/Admin | Upload file |
| GET | /api/attachments/{id} | JWT | Download file |
| DELETE | /api/attachments/{id} | GM/Admin | Delete attachment |

## Data Models

### VBU Model
```python
class VBU(TimestampMixin, Base):
    __tablename__ = "vbus"
    
    name = Column(String(255), nullable=False)
    gm_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    gm = relationship("User", foreign_keys=[gm_id])
    canvas = relationship("Canvas", back_populates="vbu", uselist=False, cascade="all, delete-orphan")
```

### Canvas Model
```python
class Canvas(TimestampMixin, Base):
    __tablename__ = "canvases"
    
    vbu_id = Column(UUID(as_uuid=True), ForeignKey("vbus.id"), unique=True, nullable=False)
    product_name = Column(String(255), nullable=True)
    lifecycle_lane = Column(Enum(LifecycleLane), nullable=False)
    success_description = Column(Text, nullable=True)
    future_state_intent = Column(Text, nullable=True)
    primary_focus = Column(String(255), nullable=True)
    resist_doing = Column(Text, nullable=True)
    good_discipline = Column(Text, nullable=True)
    primary_constraint = Column(Text, nullable=True)
    currently_testing_type = Column(Enum(CurrentlyTestingType), nullable=True)
    currently_testing_id = Column(UUID(as_uuid=True), nullable=True)
    portfolio_notes = Column(Text, nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    vbu = relationship("VBU", back_populates="canvas")
    theses = relationship("Thesis", back_populates="canvas", cascade="all, delete-orphan", order_by="Thesis.order")
```

### Thesis Model
```python
class Thesis(TimestampMixin, Base):
    __tablename__ = "theses"
    
    canvas_id = Column(UUID(as_uuid=True), ForeignKey("canvases.id"), nullable=False)
    order = Column(Integer, CheckConstraint("order >= 1 AND order <= 5"), nullable=False)
    text = Column(Text, nullable=False)
    
    # Relationships
    canvas = relationship("Canvas", back_populates="theses")
    proof_points = relationship("ProofPoint", back_populates="thesis", cascade="all, delete-orphan")
    
    __table_args__ = (UniqueConstraint("canvas_id", "order", name="uq_theses_canvas_order"),)
```

### ProofPoint Model
```python
class ProofPoint(TimestampMixin, Base):
    __tablename__ = "proof_points"
    
    thesis_id = Column(UUID(as_uuid=True), ForeignKey("theses.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ProofPointStatus), nullable=False, default=ProofPointStatus.NOT_STARTED)
    evidence_note = Column(Text, nullable=True)
    target_review_month = Column(Date, nullable=True)
    
    # Relationships
    thesis = relationship("Thesis", back_populates="proof_points")
    attachments = relationship("Attachment", back_populates="proof_point", cascade="all, delete-orphan")
```

### Attachment Model
```python
class Attachment(TimestampMixin, Base):
    __tablename__ = "attachments"
    
    proof_point_id = Column(UUID(as_uuid=True), ForeignKey("proof_points.id"), nullable=True)
    monthly_review_id = Column(UUID(as_uuid=True), ForeignKey("monthly_reviews.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(1024), nullable=False)
    content_type = Column(String(128), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    label = Column(String(255), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    proof_point = relationship("ProofPoint", back_populates="attachments")
    uploader = relationship("User")
    
    __table_args__ = (
        CheckConstraint(
            "(proof_point_id IS NOT NULL AND monthly_review_id IS NULL) OR "
            "(proof_point_id IS NULL AND monthly_review_id IS NOT NULL)",
            name="ck_attachment_single_parent"
        ),
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
        # Validate file size and type
        # Generate UUID-based storage path
        # Save file to disk
        # Create attachment record
        pass
    
    async def download(self, attachment_id: UUID) -> FileResponse:
        # Fetch attachment record
        # Return file response
        pass
    
    async def delete(self, attachment_id: UUID) -> None:
        # Delete file from disk
        # Delete attachment record
        pass
```

### CanvasService
```python
class CanvasService:
    async def get_canvas_by_vbu(self, vbu_id: UUID, db: AsyncSession) -> Canvas:
        pass
    
    async def update_canvas(self, vbu_id: UUID, canvas_data: CanvasUpdate, updated_by: UUID, db: AsyncSession) -> Canvas:
        pass
    
    async def update_currently_testing(self, canvas_id: UUID, testing_type: str, testing_id: UUID, db: AsyncSession) -> Canvas:
        pass
```

## Pydantic Schemas

### Request Schemas
```python
class VBUCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    gm_id: UUID

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
    portfolio_notes: Optional[str] = None

class ThesisCreate(BaseModel):
    text: str = Field(..., min_length=1)
    order: int = Field(..., ge=1, le=5)

class ThesisUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)

class ThesesReorder(BaseModel):
    thesis_orders: List[Dict[str, Union[UUID, int]]] = Field(..., description="List of {id, order} pairs")

class ProofPointCreate(BaseModel):
    description: str = Field(..., min_length=1)
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
    portfolio_notes: Optional[str]
    theses: List[ThesisResponse]
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
│                                                                 │
│ ┌─ Context Section ─────────────────────────────────────────┐   │
│ │ Product Name: [inline edit field]                        │   │
│ │ Lifecycle Lane: [Build] [Sell] [Milk] [Reframe]         │   │
│ │ Success Description: [inline edit textarea]              │   │
│ │ Future State Intent: [inline edit textarea]              │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Strategic Focus ──────────────────────────────────────────┐   │
│ │ Primary Focus: [inline edit field]                        │   │
│ │ Resist Doing: [inline edit textarea]                      │   │
│ │ Good Discipline: [inline edit textarea]                   │   │
│ │ Primary Constraint: [inline edit textarea]                │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Strategic Theses (max 5) ────────────────────────────────┐   │
│ │ 1. [thesis text - inline edit] [↑↓ reorder] [×]          │   │
│ │    ┌─ Proof Points ─────────────────────────────────────┐ │   │
│ │    │ • [description] [Status: In Progress ▾] [📎 files] │ │   │
│ │    │   Evidence: [inline edit]                          │ │   │
│ │    │   Target: [month picker]                           │ │   │
│ │    │ • [+ Add Proof Point]                              │ │   │
│ │    └─────────────────────────────────────────────────────┘ │   │
│ │ 2. [thesis text - inline edit] [↑↓ reorder] [×]          │   │
│ │ [+ Add Thesis]                                            │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Currently Testing ───────────────────────────────────────┐   │
│ │ Focus: [Thesis 1 ▾] or [Proof Point dropdown]            │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─ Review History ──────────────────────────────────────────┐   │
│ │ [Review entries with dates, expandable]                   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
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
}

const InlineEdit: React.FC<InlineEditProps> = ({ value, onSave, multiline, placeholder }) => {
  // Click to edit, auto-save after 2s delay, visual feedback
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
};
```

#### LaneBadge Component
```typescript
interface LaneBadgeProps {
  lane: 'build' | 'sell' | 'milk' | 'reframe';
  onChange?: (lane: string) => void;
  readonly?: boolean;
}

const LaneBadge: React.FC<LaneBadgeProps> = ({ lane, onChange, readonly }) => {
  // Colored badge with lane-specific styling
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
  // Drag & drop file upload with attachment list
};
```

## Frontend Routes

| Route | Component | Description |
|-------|-----------|-------------|
| /vbus/:id | CanvasPage | Main canvas editing interface |

## Environment Variables

Uses shared environment variables from cross-cutting.md:
- `CANVAS_UPLOAD_DIR`: File upload directory (default: /uploads)
- `CANVAS_MAX_UPLOAD_SIZE_MB`: Max upload file size (default: 10)

## Error Handling

### Validation Errors
- File too large: HTTP 413, code "FILE_TOO_LARGE"
- Unsupported file type: HTTP 415, code "UNSUPPORTED_TYPE"
- Thesis limit exceeded: HTTP 422, code "VALIDATION_ERROR"
- Invalid order values: HTTP 422, code "VALIDATION_ERROR"

### Authorization Errors
- GM accessing other's VBU: HTTP 403, code "FORBIDDEN"
- Viewer attempting edit: HTTP 403, code "FORBIDDEN"
- Portfolio notes access by non-admin: HTTP 403, code "FORBIDDEN"

### Business Logic Errors
- Canvas not found: HTTP 404, code "NOT_FOUND"
- Thesis not found: HTTP 404, code "NOT_FOUND"
- Proof point not found: HTTP 404, code "NOT_FOUND"
- Attachment not found: HTTP 404, code "NOT_FOUND"

## Testing Strategy

### Backend Tests
- Unit tests for service layer methods
- Integration tests for API endpoints with real database
- File upload/download functionality tests
- Authorization tests for role-based access

### Frontend Tests
- Component tests for InlineEdit, StatusBadge, FileUpload
- Integration tests for canvas page interactions
- Autosave functionality tests
- File upload UI tests

## Performance Considerations

- Canvas data loaded in single request with nested relationships
- File uploads processed asynchronously
- Autosave debounced to prevent excessive API calls
- Database indexes on foreign keys and frequently queried fields

## Security Considerations

- File type validation on both frontend and backend
- File size limits enforced
- Path traversal prevention in file storage
- Authorization checks on all endpoints
- CSRF protection via JWT tokens
- No sensitive data in error responses