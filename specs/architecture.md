# specs/architecture.md

## System Overview

Canvas is a lightweight web application for strategic portfolio management. General Managers maintain a single Strategy + Lifecycle Canvas per VBU/product, which rolls up into a Portfolio Dashboard for the Group Leader. The system implements a monthly review cadence that privileges evidence over activity.

## Tech Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI >=0.128.0 (async)
- **Database**: PostgreSQL 18.x
- **ORM**: SQLAlchemy >=2.0 (async with asyncpg)
- **Migrations**: Alembic >=1.14
- **Validation**: Pydantic >=2.13.0 (v2 only)
- **Auth**: JWT via python-jose + passlib
- **PDF**: WeasyPrint >=62.0
- **Logging**: structlog (JSON structured logging)
- **Testing**: pytest + httpx (async)

### Frontend
- **Framework**: React >=19.2.0 (functional components, hooks only)
- **Build**: Vite >=6.0
- **CSS**: Tailwind CSS >=4.0
- **HTTP Client**: Axios >=1.7
- **Icons**: Heroicons
- **Font**: Barlow (Google Fonts) — 300, 400, 500, 600, 700
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **Containerisation**: Docker + Docker Compose (dev + prod profiles)
- **File Storage**: Local filesystem (Docker volume mount)
- **Reverse Proxy (prod)**: Nginx (serves frontend, proxies /api)

## Port Configuration

| Service | Dev Port | Prod Port | Internal Port |
|---------|----------|-----------|---------------|
| Frontend (Vite dev) | 5173 | — | 5173 |
| Frontend (Nginx prod) | — | 80 | 80 |
| Backend (FastAPI) | 8000 | 8000 | 8000 |
| PostgreSQL | 5432 | — | 5432 |

## System Boundaries

```
┌─────────────────────────────────────────────┐
│                   Browser                    │
│  React SPA (Vite + Tailwind)                │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │Dashboard│ │VBU Page  │ │Monthly Review│ │
│  │  View   │ │(Canvas)  │ │   Wizard     │ │
│  └────┬────┘ └────┬─────┘ └──────┬───────┘ │
│       └───────────┼──────────────┘          │
│                   │ Axios (JSON)             │
└───────────────────┼─────────────────────────┘
                    │ HTTP/REST
┌───────────────────┼─────────────────────────┐
│              FastAPI Backend                  │
│  ┌──────┐ ┌──────┐ ┌────────┐ ┌──────────┐ │
│  │ Auth │ │Canvas│ │Review  │ │Portfolio │ │
│  │Routes│ │Routes│ │Routes  │ │Routes    │ │
│  └──┬───┘ └──┬───┘ └───┬────┘ └────┬─────┘ │
│     └────────┼─────────┼───────────┘        │
│              │ SQLAlchemy Async              │
│  ┌───────────┐  ┌────────────┐              │
│  │Attachment │  │PDF Export  │              │
│  │Service    │  │(WeasyPrint)│              │
│  └─────┬─────┘  └────────────┘              │
└────────┼────────────────────────────────────┘
         │
    ┌────┴─────┐
    │ /uploads │  (Docker volume)
    └──────────┘
         │
┌────────┼────────────────────────────────────┐
│    PostgreSQL 18                              │
│  users, vbus, canvases, theses,              │
│  proof_points, monthly_reviews,              │
│  commitments, attachments                    │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
canvas/
├── docker-compose.yml
├── .env.dev
├── .env.prod
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── canvas/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app factory, router mounting
│   │   ├── config.py            # Pydantic Settings from env vars
│   │   ├── db.py                # Async engine, session factory
│   │   ├── seed.py              # Dev seed data (idempotent)
│   │   ├── auth/                # Auth routes, JWT service, dependencies
│   │   ├── vbus/                # VBU CRUD routes + service
│   │   ├── canvases/            # Canvas + Thesis + ProofPoint routes + service
│   │   ├── reviews/             # MonthlyReview + Commitment routes + service
│   │   ├── portfolio/           # Dashboard aggregation + portfolio notes
│   │   ├── attachments/         # File upload/download routes + service
│   │   ├── pdf/                 # WeasyPrint PDF export service + templates
│   │   └── models/              # SQLAlchemy models (one file per entity)
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/client.ts        # Axios instance with interceptors
│       ├── auth/                # Login page, useAuth hook
│       ├── dashboard/           # Portfolio dashboard, VBU table, filters
│       ├── canvas/              # Canvas page, section components
│       ├── reviews/             # Review wizard, review history
│       ├── admin/               # User management (admin only)
│       ├── components/          # Shared: AppShell, StatusBadge, LaneBadge, etc.
│       └── styles/index.css     # Tailwind entry point
└── specs/
```

## API Conventions

### URL Pattern
```
/api/auth/{action}                    # Auth endpoints (no versioning)
/api/{resource}                       # List, Create
/api/{resource}/{id}                  # Retrieve, Update, Delete
/api/{parent}/{parent_id}/{resource}  # Nested resources
```

### Response Envelope — Success
```json
{
  "data": { ... },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

### Response Envelope — List
```json
{
  "data": [ ... ],
  "meta": { "total": 42, "page": 1, "per_page": 25, "timestamp": "..." }
}
```

### Response Envelope — Error
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
| CONFLICT | 409 | Duplicate resource (e.g., email) |
| FILE_TOO_LARGE | 413 | Upload exceeds 10MB |
| UNSUPPORTED_TYPE | 415 | File type not in allowed list |
| INTERNAL_ERROR | 500 | Unexpected server error |

## Authentication Flow

1. User submits email + password to `POST /api/auth/login`
2. Backend verifies credentials via passlib bcrypt, returns `{ access_token, refresh_token, token_type }`
3. Frontend stores access token in memory, refresh token in httpOnly cookie
4. All API requests include `Authorization: Bearer {access_token}`
5. On 401, frontend calls `POST /api/auth/refresh` with refresh token cookie
6. Backend middleware extracts user from JWT, attaches to `request.state.user`
7. Route-level dependency functions check `role` for authorization
8. GM routes additionally verify `vbu.gm_id == current_user.id`

## Authorization Matrix

| Resource | Admin | GM (own) | GM (other) | Viewer |
|----------|-------|----------|------------|--------|
| VBU list | All | Own only | — | All (read) |
| VBU create/delete | ✅ | ❌ | ❌ | ❌ |
| Canvas read | All | Own | ❌ | All |
| Canvas write | All | Own | ❌ | ❌ |
| Monthly review create | All | Own | ❌ | ❌ |
| Portfolio notes | ✅ | ❌ | ❌ | ❌ |
| User management | ✅ | ❌ | ❌ | ❌ |
| File upload | All | Own | ❌ | ❌ |
| PDF export | All | Own | ❌ | All |

## Shared Patterns

### Backend — Base Model Mixin
```python
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

class TimestampMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

### Backend — Response Helpers
```python
from datetime import datetime, timezone

def success_response(data, status_code=200):
    return {"data": data, "meta": {"timestamp": datetime.now(timezone.utc).isoformat()}}

def list_response(data, total, page=1, per_page=25):
    return {"data": data, "meta": {"total": total, "page": page, "per_page": per_page, "timestamp": datetime.now(timezone.utc).isoformat()}}
```

### Backend — Auth Dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)):
    # Decode JWT, fetch user, raise 401 if invalid
    ...

def require_role(*roles):
    async def checker(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
```

### Frontend — API Client
```typescript
import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
    }
    return Promise.reject(error);
  }
);
```

## External Integrations

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| Google Fonts | Barlow font loading | None (public CDN) |

No external API integrations in v1. All data is self-contained.

## Testing Strategy

| Layer | Tool | Target Coverage |
|-------|------|----------------|
| Backend unit/integration | pytest + httpx | 80% |
| Frontend component | Vitest + React Testing Library | 70% |
| Database | Real PostgreSQL in Docker | — |
| Mocking policy | Integration-first; real DB, no mocks for data layer | — |

## Decisions Log

| Decision | Rationale | Date |
|----------|-----------|------|
| No API versioning prefix | Single-org pilot, no external consumers | 2026-02-13 |
| JWT in memory + httpOnly refresh cookie | Balance between security and UX | 2026-02-13 |
| WeasyPrint for PDF | Python-native, no external service needed | 2026-02-13 |
| No component library | Small app, Tailwind utility classes sufficient | 2026-02-13 |
| Polymorphic currently_testing FK | Simpler than separate join tables for thesis/proof_point | 2026-02-13 |
| Single org, no multi-tenancy | Pilot scope, simplifies auth model | 2026-02-13 |
