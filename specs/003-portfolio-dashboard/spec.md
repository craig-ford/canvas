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
- Admin/Viewer see all VBUs, GM sees only their own VBUs
- Each VBU includes: name, lifecycle_lane, success_description, currently_testing, next_review_date, primary_constraint, health_indicator
- Health indicator computed as: any stalled → "At Risk"; all not_started → "Not Started"; any observed & none stalled → "On Track"; else → "In Progress"
- Response follows standard envelope format with timestamp

### FR-002: Portfolio Filtering
**Description:** Filter VBUs by lifecycle lane, GM, and proof point health status
**Acceptance Criteria:**
- Query parameters: lane, gm_id, health_status
- Multiple values supported (comma-separated)
- Filters applied with AND logic
- Empty filters return all visible VBUs

### FR-003: Portfolio Notes Management
**Description:** Admin-only free text panel for portfolio-level notes
**Acceptance Criteria:**
- PATCH /api/portfolio/notes endpoint (admin only)
- Notes stored in canvas.portfolio_notes field
- Notes visible to all users but editable only by admin
- Autosave functionality on frontend

### FR-004: Canvas PDF Export
**Description:** Export individual canvas as PDF using WeasyPrint
**Acceptance Criteria:**
- GET /api/vbus/{vbu_id}/canvas/pdf returns PDF file
- PDF includes all canvas sections: context, theses, proof points, constraints
- Styled with Canvas brand colors and typography
- File download with proper Content-Type and filename headers

### FR-005: Dashboard UI Components
**Description:** React components for portfolio dashboard page
**Acceptance Criteria:**
- VBU table with sortable columns
- Filter controls for lane, GM, health status
- Portfolio notes panel (admin only)
- Export buttons for individual VBUs
- Responsive design for mobile/tablet
- Click-through navigation to VBU detail pages

## Technical Requirements

### Backend Components

#### Portfolio Service
```python
class PortfolioService:
    async def get_summary(self, user: User, filters: PortfolioFilters) -> List[VBUSummary]
    async def update_portfolio_notes(self, notes: str, user: User) -> None
    
    def _compute_health_indicator(self, proof_points: List[ProofPoint]) -> str
```

#### PDF Service (implements cross-cutting interface)
```python
class PDFService:
    async def export_canvas(self, canvas_id: UUID) -> bytes
```

#### API Routes
```python
# canvas/portfolio/router.py
@router.get("/summary")
async def get_portfolio_summary(
    lane: Optional[str] = None,
    gm_id: Optional[str] = None, 
    health_status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
)

@router.patch("/notes")
async def update_portfolio_notes(
    request: PortfolioNotesRequest,
    current_user: User = Depends(require_role("admin"))
)

@router.get("/vbus/{vbu_id}/canvas/pdf")
async def export_canvas_pdf(
    vbu_id: UUID,
    current_user: User = Depends(get_current_user)
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
```

#### Portfolio Filters
```python
class PortfolioFilters(BaseModel):
    lane: Optional[List[LifecycleLane]] = None
    gm_id: Optional[List[UUID]] = None
    health_status: Optional[List[str]] = None
```

### Frontend Components

#### Dashboard Page Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Portfolio Dashboard                                         │
├─────────────────────────────────────────────────────────────┤
│ Filters: [Lane ▾] [GM ▾] [Health ▾]           [Clear All]  │
├─────────────────────────────────────────────────────────────┤
│ VBU Table:                                                  │
│ ┌─────────┬──────┬─────────┬──────────┬────────┬─────────┐ │
│ │ VBU     │ Lane │ GM      │ Testing  │ Health │ Actions │ │
│ ├─────────┼──────┼─────────┼──────────┼────────┼─────────┤ │
│ │ Product │ Build│ John    │ Thesis 1 │ 🟡 IP  │ [PDF]   │ │
│ │ A       │      │ Smith   │          │        │ [View]  │ │
│ └─────────┴──────┴─────────┴──────────┴────────┴─────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Portfolio Notes (Admin Only):                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Free text area with autosave]                         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components
- `DashboardPage.tsx` - Main page container
- `VBUTable.tsx` - Sortable table with VBU data
- `DashboardFilters.tsx` - Filter controls
- `PortfolioNotes.tsx` - Admin notes panel
- `HealthIndicator.tsx` - Status badge component
- `LaneBadge.tsx` - Lifecycle lane badge

### Health Indicator Logic
```python
def compute_health_indicator(proof_points: List[ProofPoint]) -> str:
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

### PDF Template Structure
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Canvas brand colors and Barlow font */
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Barlow', sans-serif; }
        .header { color: #008AB0; }
        .lane-build { background-color: #B3E0ED; }
        /* ... other styles */
    </style>
</head>
<body>
    <div class="canvas-export">
        <h1>{{ vbu_name }} - Strategy Canvas</h1>
        <div class="lane-badge lane-{{ lifecycle_lane }}">{{ lifecycle_lane|title }}</div>
        
        <section class="context">
            <h2>Context & Intent</h2>
            <p>{{ success_description }}</p>
            <p>{{ future_state_intent }}</p>
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
        
        <section class="constraints">
            <h2>Primary Constraint</h2>
            <p>{{ primary_constraint }}</p>
        </section>
    </div>
</body>
</html>
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/portfolio/summary | JWT | Get dashboard summary with filters |
| PATCH | /api/portfolio/notes | Admin | Update portfolio notes |
| GET | /api/vbus/{vbu_id}/canvas/pdf | JWT | Export canvas as PDF |

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

## UI Components

### Dashboard Filters
```typescript
interface FilterState {
  lanes: LifecycleLane[];
  gmIds: string[];
  healthStatuses: string[];
}

const DashboardFilters: React.FC<{
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  gms: User[];
}> = ({ filters, onFiltersChange, gms }) => {
  return (
    <div className="flex gap-4 mb-6">
      <MultiSelect
        label="Lifecycle Lane"
        options={LIFECYCLE_LANES}
        values={filters.lanes}
        onChange={(lanes) => onFiltersChange({ ...filters, lanes })}
      />
      <MultiSelect
        label="General Manager"
        options={gms.map(gm => ({ value: gm.id, label: gm.name }))}
        values={filters.gmIds}
        onChange={(gmIds) => onFiltersChange({ ...filters, gmIds })}
      />
      <MultiSelect
        label="Health Status"
        options={HEALTH_STATUSES}
        values={filters.healthStatuses}
        onChange={(healthStatuses) => onFiltersChange({ ...filters, healthStatuses })}
      />
      <button onClick={() => onFiltersChange({ lanes: [], gmIds: [], healthStatuses: [] })}>
        Clear All
      </button>
    </div>
  );
};
```

### VBU Table
```typescript
const VBUTable: React.FC<{
  vbus: VBUSummary[];
  onExportPDF: (vbuId: string) => void;
  onViewVBU: (vbuId: string) => void;
}> = ({ vbus, onExportPDF, onViewVBU }) => {
  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-left p-3">VBU</th>
          <th className="text-left p-3">Lane</th>
          <th className="text-left p-3">GM</th>
          <th className="text-left p-3">Currently Testing</th>
          <th className="text-left p-3">Health</th>
          <th className="text-left p-3">Actions</th>
        </tr>
      </thead>
      <tbody>
        {vbus.map(vbu => (
          <tr key={vbu.id} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="p-3">
              <div>
                <div className="font-medium">{vbu.name}</div>
                <div className="text-sm text-gray-600">{vbu.success_description}</div>
              </div>
            </td>
            <td className="p-3">
              <LaneBadge lane={vbu.lifecycle_lane} />
            </td>
            <td className="p-3">{vbu.gm_name}</td>
            <td className="p-3">{vbu.currently_testing}</td>
            <td className="p-3">
              <HealthIndicator status={vbu.health_indicator} />
            </td>
            <td className="p-3">
              <div className="flex gap-2">
                <button 
                  onClick={() => onExportPDF(vbu.id)}
                  className="text-sm bg-teal-600 text-white px-2 py-1 rounded"
                >
                  PDF
                </button>
                <button 
                  onClick={() => onViewVBU(vbu.id)}
                  className="text-sm bg-gray-600 text-white px-2 py-1 rounded"
                >
                  View
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

### Health Indicator Badge
```typescript
const HealthIndicator: React.FC<{ status: string }> = ({ status }) => {
  const styles = {
    "Not Started": "bg-gray-100 text-gray-600",
    "In Progress": "bg-teal-100 text-teal-700", 
    "On Track": "bg-green-100 text-green-700",
    "At Risk": "bg-yellow-100 text-yellow-700"
  };
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
      {status}
    </span>
  );
};
```

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
└── hooks/
    └── usePortfolio.ts
```

## Testing Requirements

### Backend Tests
- Portfolio summary endpoint with role-based filtering
- Health indicator computation logic
- PDF generation with proper styling
- Portfolio notes update (admin only)

### Frontend Tests  
- Dashboard page renders VBU table
- Filters update query parameters
- Portfolio notes autosave (admin only)
- PDF export triggers download
- Health indicator displays correct colors

## Security Considerations

- Portfolio notes restricted to admin role
- VBU visibility filtered by user role (GM sees own only)
- PDF export respects same access controls as canvas view
- File download uses secure headers and content-type

## Performance Considerations

- Portfolio summary query optimized with proper indexes
- PDF generation cached for repeated requests
- Frontend table virtualization for large VBU lists
- Debounced autosave for portfolio notes

## Error Handling

- 403 Forbidden for non-admin portfolio notes access
- 404 Not Found for invalid VBU IDs in PDF export
- PDF generation errors return 500 with user-friendly message
- Filter validation errors return 422 with field details