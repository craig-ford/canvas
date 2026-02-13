# Feature 003: Portfolio Dashboard

## Overview

The Portfolio Dashboard provides an aggregated view of all VBUs with strategic health indicators, filtering capabilities, and PDF export functionality. It serves as the primary landing page for all user roles, showing VBU name, lifecycle lane, success description, currently testing focus, next review date, primary constraint, and computed proof point health indicators.

## Dependencies

- **001-auth**: User authentication and role-based access control
- **002-canvas-management**: Canvas data model and VBU entities

## Functional Requirements

### FR-001: Portfolio Summary Endpoint
**Description:** API endpoint that aggregates VBU data with computed health indicators
**Acceptance Criteria:**
- GET /api/portfolio/summary returns all VBUs visible to current user
- Admin/Viewer see all VBUs, GM sees only their own VBUs (WHERE gm_id = current_user.id)
- Each VBU includes: name, lifecycle_lane, success_description, currently_testing, next_review_date, primary_constraint, health_indicator
- Health indicator computed as: any stalled → "At Risk"; all not_started → "Not Started"; any observed & none stalled → "On Track"; else → "In Progress"
- Response follows standard envelope format with timestamp
- Performance target: <200ms for 50 VBUs, <1000ms for 500 VBUs

### FR-002: Portfolio Filtering
**Description:** Filter VBUs by lifecycle lane, GM, and proof point health status
**Acceptance Criteria:**
- Query parameters: lane, gm_id, health_status (comma-separated values)
- Multiple values within parameter use OR logic, different parameters use AND logic
- Filters applied with proper SQL WHERE clauses for performance
- Empty filters return all visible VBUs
- Invalid enum values return 422 with validation details

### FR-003: Portfolio Notes Management
**Description:** Admin-only free text panel for portfolio-level notes
**Acceptance Criteria:**
- PATCH /api/portfolio/notes endpoint (admin only)
- Notes stored in canvas.portfolio_notes field, max 10,000 characters
- Notes visible to all users but editable only by admin
- Autosave functionality with 500ms debounce on frontend
- HTML entity encoding for XSS prevention

### FR-004: Canvas PDF Export
**Description:** Export individual canvas as PDF using WeasyPrint
**Acceptance Criteria:**
- GET /api/vbus/{vbu_id}/canvas/pdf returns PDF file
- PDF includes all canvas sections: context, theses, proof points, constraints
- Styled with Canvas brand colors (#008AB0 headers) and Barlow font
- File download with proper Content-Type and filename headers
- Performance target: <2s for typical canvas, <5s for complex canvas
- Access control: GM can only export own VBUs

### FR-005: Dashboard UI Components
**Description:** React components for portfolio dashboard page
**Acceptance Criteria:**
- Responsive design: table layout (1200px+), card layout (768px-1199px), list layout (320px-767px)
- VBU table with sortable columns and pagination (25 per page)
- Filter controls with multi-select dropdowns
- Portfolio notes panel with autosave indicator (admin only)
- Export buttons for individual VBUs
- Loading, empty, and error states with proper ARIA labels
- Click-through navigation to VBU detail pages

## Technical Requirements

### Backend Components

#### Portfolio Service
```python
class PortfolioService:
    async def get_summary(self, user: User, filters: PortfolioFilters) -> List[VBUSummary]:
        """Get portfolio summary with role-based filtering and health computation"""
        # Optimized query with early filtering
        where_conditions = ["1=1"]
        params = {}
        
        if user.role == "gm":
            where_conditions.append("v.gm_id = :user_id")
            params["user_id"] = user.id
        
        if filters.lane:
            where_conditions.append("c.lifecycle_lane = ANY(:lanes)")
            params["lanes"] = filters.lane
        
        # Use materialized health indicators for performance
        query = f"""
        SELECT v.id, v.name, u.name as gm_name, c.lifecycle_lane,
               c.success_description, c.primary_constraint, c.portfolio_notes,
               cct.currently_testing_text,
               COALESCE(c.health_indicator_cache, 'Not Started') as health_indicator
        FROM vbus v
        JOIN users u ON v.gm_id = u.id  
        JOIN canvases c ON c.vbu_id = v.id
        LEFT JOIN canvas_currently_testing cct ON cct.canvas_id = c.id
        WHERE {' AND '.join(where_conditions)}
        """
        
        result = await db.execute(text(query), params)
        return [VBUSummary.from_row(row) for row in result]
    
    async def update_portfolio_notes(self, notes: str, user: User) -> None:
        """Update portfolio notes (admin only)"""
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
        
        # HTML entity encoding for security
        sanitized_notes = html.escape(notes) if notes else None
        
        # Update all canvases with new portfolio notes
        await db.execute(
            update(Canvas).values(
                portfolio_notes=sanitized_notes,
                updated_at=func.now(),
                updated_by=user.id
            )
        )
    
    def _compute_health_indicator(self, proof_points: List[ProofPoint]) -> str:
        """Compute health indicator from proof point statuses"""
        if not proof_points:
            return "Not Started"
        
        statuses = [pp.status for pp in proof_points]
        
        if "stalled" in statuses:
            return "At Risk"
        elif all(status == "not_started" for status in statuses):
            return "Not Started"  
        elif "observed" in statuses and "stalled" not in statuses:
            return "On Track"
        else:
            return "In Progress"
```

#### PDF Service (implements cross-cutting interface)
```python
class PDFService:
    async def export_canvas(self, canvas_id: UUID) -> bytes:
        """Export canvas as PDF with proper styling"""
        canvas = await self._get_canvas_with_relations(canvas_id)
        
        template = self.jinja_env.get_template("canvas.html")
        html_content = template.render(
            vbu_name=canvas.vbu.name,
            lifecycle_lane=canvas.lifecycle_lane,
            success_description=canvas.success_description,
            future_state_intent=canvas.future_state_intent,
            theses=canvas.theses,
            primary_constraint=canvas.primary_constraint
        )
        
        # Generate PDF with WeasyPrint
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
```

#### API Routes
```python
# canvas/portfolio/router.py
@router.get("/summary")
async def get_portfolio_summary(
    lane: Optional[str] = Query(None, description="Comma-separated lifecycle lanes"),
    gm_id: Optional[str] = Query(None, description="Comma-separated GM UUIDs"), 
    health_status: Optional[str] = Query(None, description="Comma-separated health statuses"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get portfolio summary with filtering"""
    filters = PortfolioFilters(
        lane=lane.split(",") if lane else None,
        gm_id=[UUID(id.strip()) for id in gm_id.split(",")] if gm_id else None,
        health_status=health_status.split(",") if health_status else None
    )
    
    summary = await portfolio_service.get_summary(current_user, filters)
    return list_response(summary, len(summary))

@router.patch("/notes")
async def update_portfolio_notes(
    request: PortfolioNotesRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Update portfolio notes (admin only)"""
    await portfolio_service.update_portfolio_notes(request.notes, current_user)
    return success_response({
        "notes": request.notes,
        "updated_at": datetime.now(timezone.utc).isoformat()
    })

@router.get("/vbus/{vbu_id}/canvas/pdf")
async def export_canvas_pdf(
    vbu_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """Export canvas as PDF"""
    # Verify access to VBU
    vbu = await vbu_service.get_by_id(vbu_id, current_user)
    if not vbu:
        raise HTTPException(status_code=404, detail="VBU not found")
    
    pdf_bytes = await pdf_service.export_canvas(vbu.canvas.id)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{vbu.name}_canvas.pdf"',
            "Content-Length": str(len(pdf_bytes))
        }
    )
```

### Data Models

#### VBU Summary Response
```python
class VBUSummary(BaseModel):
    id: UUID
    name: str
    gm_name: str
    lifecycle_lane: LifecycleLane
    success_description: Optional[str]
    currently_testing: Optional[str]
    next_review_date: Optional[date]
    primary_constraint: Optional[str]
    health_indicator: str  # "Not Started" | "In Progress" | "On Track" | "At Risk"
    portfolio_notes: Optional[str]

class PortfolioFilters(BaseModel):
    lane: Optional[List[LifecycleLane]] = None
    gm_id: Optional[List[UUID]] = None
    health_status: Optional[List[str]] = None

class PortfolioNotesRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=10000)
```

### Frontend Components

#### Dashboard Page Structure (Desktop 1200px+)
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Canvas                                                    [User Menu ▾] [Logout]        │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Portfolio Dashboard                                                                     │
│                                                                                         │
│ ┌─ Filters ─────────────────────────────────────────────────────────────────────────┐ │
│ │ [Lane ▾] [GM ▾] [Health ▾]                                    [Clear All] [Export] │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│ ┌─ VBU Table ───────────────────────────────────────────────────────────────────────┐ │
│ │ ┌─────────────┬──────┬─────────┬──────────────┬────────────┬─────────┬─────────┐ │ │
│ │ │ VBU Name ↕  │Lane ↕│ GM ↕    │ Testing ↕    │ Next Rev ↕ │Health ↕ │Actions  │ │ │
│ │ ├─────────────┼──────┼─────────┼──────────────┼────────────┼─────────┼─────────┤ │ │
│ │ │ Product A   │BUILD │J.Smith  │ Acquisition  │ 2026-03-15 │🟡 IP    │[PDF][→] │ │ │
│ │ │ Success...  │      │         │ channels     │            │         │         │ │ │
│ │ └─────────────┴──────┴─────────┴──────────────┴────────────┴─────────┴─────────┘ │ │
│ │ Showing 2 of 15 VBUs                                           [1][2][3]...[Next] │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│ ┌─ Portfolio Notes (Admin Only) ────────────────────────────────────────────────────┐ │
│ │ ┌─────────────────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Q1 focus areas: Product A scaling, Product B optimization...                   │ │ │
│ │ └─────────────────────────────────────────────────────────────────────────────────┘ │ │
│ │ ✓ Saved 2 seconds ago                                                              │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Key Components
```typescript
// Dashboard page with responsive layout
const DashboardPage: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    lanes: [], gmIds: [], healthStatuses: []
  });
  const [vbus, setVBUs] = useState<VBUSummary[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Fetch portfolio data with filters
  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (filters.lanes.length) params.set('lane', filters.lanes.join(','));
        if (filters.gmIds.length) params.set('gm_id', filters.gmIds.join(','));
        if (filters.healthStatuses.length) params.set('health_status', filters.healthStatuses.join(','));
        
        const response = await api.get(`/portfolio/summary?${params}`);
        setVBUs(response.data.data);
      } catch (error) {
        // Handle error state
      } finally {
        setLoading(false);
      }
    };
    
    fetchPortfolio();
  }, [filters]);
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Portfolio Dashboard</h1>
      
      <DashboardFilters 
        filters={filters} 
        onFiltersChange={setFilters}
      />
      
      {loading ? (
        <LoadingState />
      ) : vbus.length === 0 ? (
        <EmptyState onClearFilters={() => setFilters({lanes: [], gmIds: [], healthStatuses: []})} />
      ) : (
        <VBUTable 
          vbus={vbus}
          onExportPDF={handlePDFExport}
          onViewVBU={handleViewVBU}
        />
      )}
      
      <PortfolioNotes />
    </div>
  );
};

// Health indicator with proper accessibility
const HealthIndicator: React.FC<{ status: string }> = ({ status }) => {
  const config = {
    "Not Started": { color: "bg-gray-100 text-gray-600", icon: "⚪", label: "Not Started" },
    "In Progress": { color: "bg-teal-100 text-teal-700", icon: "🟡", label: "In Progress" },
    "On Track": { color: "bg-green-100 text-green-700", icon: "🟢", label: "On Track" },
    "At Risk": { color: "bg-yellow-100 text-yellow-700", icon: "🔴", label: "At Risk" }
  };
  
  const { color, icon, label } = config[status] || config["Not Started"];
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      <span className="sr-only">Health status: </span>
      <span aria-label={label}>{icon} {status}</span>
    </span>
  );
};

// Portfolio notes with autosave
const PortfolioNotes: React.FC = () => {
  const { user } = useAuth();
  const [notes, setNotes] = useState('');
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved');
  
  // Debounced autosave
  const debouncedSave = useCallback(
    debounce(async (value: string) => {
      if (user?.role !== 'admin') return;
      
      setSaveStatus('saving');
      try {
        await api.patch('/portfolio/notes', { notes: value });
        setSaveStatus('saved');
      } catch (error) {
        setSaveStatus('error');
      }
    }, 500),
    [user]
  );
  
  const handleNotesChange = (value: string) => {
    setNotes(value);
    debouncedSave(value);
  };
  
  if (user?.role !== 'admin') return null;
  
  return (
    <div className="mt-6" role="region" aria-label="Portfolio notes">
      <h2 className="text-lg font-semibold mb-2">Portfolio Notes</h2>
      <textarea
        value={notes}
        onChange={(e) => handleNotesChange(e.target.value)}
        className="w-full h-32 p-3 border rounded-md"
        placeholder="Add portfolio-level notes..."
        aria-label="Portfolio notes (admin only)"
        aria-describedby="notes-status"
        maxLength={10000}
      />
      <div id="notes-status" aria-live="polite" className="text-sm text-gray-500 mt-1">
        {saveStatus === 'saved' && '✓ Saved'}
        {saveStatus === 'saving' && '⟳ Saving...'}
        {saveStatus === 'error' && '⚠ Error saving'}
      </div>
    </div>
  );
};
```

### Database Optimizations

#### Required Indexes
```sql
-- Primary dashboard query optimization
CREATE INDEX ix_portfolio_dashboard_main ON vbus (gm_id) INCLUDE (name);
CREATE INDEX ix_canvases_portfolio_summary ON canvases (vbu_id, lifecycle_lane, health_indicator_cache);
CREATE INDEX ix_proof_points_health_agg ON proof_points (thesis_id, status);

-- Health indicator materialization
ALTER TABLE canvases ADD COLUMN health_indicator_cache VARCHAR(20);
ALTER TABLE canvases ADD COLUMN health_computed_at TIMESTAMPTZ;

-- Trigger for health indicator updates
CREATE OR REPLACE FUNCTION update_canvas_health_indicator()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE canvases 
    SET health_indicator_cache = (
        CASE 
            WHEN EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                       WHERE t.canvas_id = c.id AND pp.status = 'stalled') THEN 'At Risk'
            WHEN NOT EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                           WHERE t.canvas_id = c.id AND pp.status != 'not_started') THEN 'Not Started'
            WHEN EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                       WHERE t.canvas_id = c.id AND pp.status = 'observed') 
                 AND NOT EXISTS(SELECT 1 FROM proof_points pp JOIN theses t ON pp.thesis_id = t.id 
                               WHERE t.canvas_id = c.id AND pp.status = 'stalled') THEN 'On Track'
            ELSE 'In Progress'
        END
    ),
    health_computed_at = NOW()
    FROM canvases c
    JOIN theses t ON t.canvas_id = c.id
    WHERE t.id = COALESCE(NEW.thesis_id, OLD.thesis_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER proof_point_health_update
    AFTER INSERT OR UPDATE OR DELETE ON proof_points
    FOR EACH ROW EXECUTE FUNCTION update_canvas_health_indicator();
```

### PDF Template
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&display=swap');
        body { 
            font-family: 'Barlow', sans-serif; 
            margin: 0; 
            padding: 20px;
            color: #1A1A1A;
        }
        .header { 
            color: #008AB0; 
            border-bottom: 2px solid #008AB0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .lane-build { background-color: #B3E0ED; color: #006F8E; }
        .lane-sell { background-color: #E8F4D9; color: #5A7C2A; }
        .lane-milk { background-color: #E8EAF5; color: #1E2875; }
        .lane-reframe { background-color: #FFFBE6; color: #9BA800; }
        .lane-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .thesis {
            margin-bottom: 20px;
            border-left: 3px solid #008AB0;
            padding-left: 15px;
        }
        .proof-point {
            margin: 10px 0;
            padding: 8px;
            border-radius: 4px;
        }
        .status-not_started { background-color: #F5F5F5; }
        .status-in_progress { background-color: #B3E0ED; }
        .status-observed { background-color: #E8F4D9; }
        .status-stalled { background-color: #FFFBE6; }
    </style>
</head>
<body>
    <div class="canvas-export">
        <div class="header">
            <h1>{{ vbu_name }} - Strategy Canvas</h1>
            <div class="lane-badge lane-{{ lifecycle_lane }}">{{ lifecycle_lane|title }}</div>
        </div>
        
        <section class="context">
            <h2>Context & Intent</h2>
            {% if success_description %}
            <p><strong>Success Description:</strong> {{ success_description }}</p>
            {% endif %}
            {% if future_state_intent %}
            <p><strong>Future State Intent:</strong> {{ future_state_intent }}</p>
            {% endif %}
        </section>
        
        <section class="theses">
            <h2>Strategic Theses</h2>
            {% for thesis in theses %}
            <div class="thesis">
                <h3>{{ thesis.order }}. {{ thesis.text }}</h3>
                <div class="proof-points">
                    {% for pp in thesis.proof_points %}
                    <div class="proof-point status-{{ pp.status }}">
                        <strong>{{ pp.description }}</strong>
                        {% if pp.evidence_note %}
                        <p>{{ pp.evidence_note }}</p>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </section>
        
        {% if primary_constraint %}
        <section class="constraints">
            <h2>Primary Constraint</h2>
            <p>{{ primary_constraint }}</p>
        </section>
        {% endif %}
    </div>
</body>
</html>
```

## API Endpoints

| Method | Path | Auth | Description | Performance Target |
|--------|------|------|-------------|-------------------|
| GET | /api/portfolio/summary | JWT | Get dashboard summary with filters | <200ms (50 VBUs) |
| PATCH | /api/portfolio/notes | Admin | Update portfolio notes | <100ms |
| GET | /api/vbus/{vbu_id}/canvas/pdf | JWT | Export canvas as PDF | <2s (typical) |

### Response Examples

#### Portfolio Summary
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Product Alpha",
      "gm_name": "John Smith", 
      "lifecycle_lane": "build",
      "success_description": "In this lane, success means validated product-market fit",
      "currently_testing": "Customer acquisition channels",
      "next_review_date": "2026-03-15",
      "primary_constraint": "Limited engineering capacity",
      "health_indicator": "In Progress",
      "portfolio_notes": "Focus area for Q1"
    }
  ],
  "meta": {
    "total": 1,
    "timestamp": "2026-02-13T14:00:00Z"
  }
}
```

## Security & Access Control

### Authentication
- All endpoints require valid JWT token via `Authorization: Bearer {token}` header
- Access token expires in 30 minutes with refresh token rotation

### Authorization Matrix
| Action | Admin | GM | Viewer |
|--------|-------|----|---------| 
| View portfolio summary | All VBUs | Own VBUs only | All VBUs (read-only) |
| Edit portfolio notes | ✅ | ❌ | ❌ |
| Export canvas PDF | All VBUs | Own VBUs only | All VBUs |

### Data Protection
- Portfolio notes HTML entity encoded to prevent XSS
- GM access filtered at database level: `WHERE vbu.gm_id = current_user.id`
- Error responses never expose unauthorized VBU details
- Rate limiting: 60 requests/minute per user for summary endpoint

### Audit Logging
| Event | Data Logged | Retention |
|-------|-------------|-----------|
| Portfolio notes update | user_id, timestamp, notes_length | 7 years |
| PDF export | user_id, vbu_id, timestamp, file_size | 1 year |
| Unauthorized access attempt | user_id, requested_vbu_id, timestamp | 2 years |

## Testing Requirements

### Backend Tests
- Portfolio summary with role-based filtering (admin sees all, GM sees own)
- Health indicator computation with all status combinations
- PDF generation with proper styling and error handling
- Portfolio notes update with admin-only access control
- Filter validation and SQL injection prevention

### Frontend Tests  
- Dashboard page renders with loading/empty/error states
- Filters update URL parameters and trigger API calls
- Portfolio notes autosave with proper debouncing (admin only)
- PDF export triggers download with success/error feedback
- Accessibility: keyboard navigation, ARIA labels, screen reader support

### Performance Tests
- Portfolio summary <200ms for 50 VBUs, <1000ms for 500 VBUs
- PDF generation <2s for typical canvas, <5s for complex canvas
- Concurrent user load testing (100 simultaneous requests)

## File Structure

```
backend/canvas/portfolio/
├── __init__.py
├── router.py          # FastAPI routes
├── service.py         # Business logic
└── schemas.py         # Pydantic models

backend/canvas/pdf/
├── __init__.py
├── service.py         # WeasyPrint PDF generation
└── templates/
    └── canvas.html    # PDF template

frontend/src/dashboard/
├── DashboardPage.tsx
├── VBUTable.tsx
├── DashboardFilters.tsx
├── PortfolioNotes.tsx
├── HealthIndicator.tsx
└── hooks/
    └── usePortfolio.ts
```

## Error Handling

### API Error Responses
- 401 Unauthorized: Missing/invalid JWT token
- 403 Forbidden: Non-admin accessing portfolio notes, GM accessing other's VBU
- 404 Not Found: Invalid VBU ID (same response for non-existent and unauthorized)
- 422 Validation Error: Invalid filter parameters, notes too long
- 500 Internal Error: Database connection failure, PDF generation failure

### Frontend Error States
- Network errors: Retry button with exponential backoff
- Empty results: Clear filters suggestion with helpful messaging
- PDF export errors: Toast notification with specific error message
- Loading timeouts: Graceful degradation with partial data display