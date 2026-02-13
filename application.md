# Canvas — Strategy Portfolio Dashboard

## Overview

Canvas is a lightweight web application that lets General Managers (GMs) maintain a single "living" Strategy + Lifecycle Canvas per VBU (Virtual Business Unit) or product, and rolls those canvases up into a Portfolio Dashboard for the Group Leader. The system implements a Strategy Implementation Methodology (Intent → Theses → Proof Points → Monthly review loop) and strongly privileges **evidence over activity**. It makes the monthly review cadence easy to run and keeps strategy alive without constant rewrites.

## Goals

1. Each GM maintains one Canvas per VBU/product capturing: lifecycle lane, future state intent, strategic theses, proof points, constraints, and cadence commitments.
2. The Group Leader sees a Portfolio Dashboard showing all VBUs at a glance — lifecycle lanes, what's being tested, proof point health, constraints, and next review dates.
3. Monthly reviews are structured and repeatable — a guided wizard walks GMs through four prompts and captures dated review entries.
4. The system privileges evidence over activity — proof points are observable signals, not task lists.
5. Frictionless editing — inline edit with autosave, minimal clicks to update a canvas.

## Out of Scope

- Multi-organisation / SaaS tenancy — single organisation only. GMs log in individually and see only their own VBUs via role-based access control.
- Notifications / email reminders — out of scope for v1.
- AI-powered analysis or recommendations.
- Integration with external project management tools (Jira, Asana, etc.).
- Mobile native apps — responsive web only.
- Internationalisation (i18n).

## User Roles

| Role | Permissions | Default Landing Page |
|------|------------|---------------------|
| Admin | View/edit all VBUs, all canvases, all reviews. Manage users. Assign GMs to VBUs. Portfolio notes panel. | Portfolio Dashboard |
| GM | View/edit their own VBU(s) and canvases only. Create/complete monthly reviews for their VBUs. Cannot see other GMs' data. | Portfolio Dashboard (filtered to own VBUs) |
| Viewer | Read-only access to all VBUs, canvases, and reviews. | Portfolio Dashboard |

## Technology Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Backend Framework | FastAPI | >=0.128.0 | Python 3.12+, async |
| Data Validation | Pydantic | >=2.13.0 | v2 only, no v1 compat needed |
| Database | PostgreSQL | 18.x | Primary data store |
| ORM | SQLAlchemy | >=2.0 | Async with asyncpg driver |
| Migrations | Alembic | >=1.14 | Auto-generate from models |
| Frontend Framework | React | >=19.2.0 | Functional components, hooks only |
| Build Tool | Vite | >=6.0 | Fast dev server, HMR |
| CSS Framework | Tailwind CSS | >=4.0 | Utility-first |
| HTTP Client | Axios | >=1.7 | API calls from frontend |
| Auth | JWT | via python-jose + passlib | Email/password for pilot |
| File Storage | Local filesystem | — | Docker volume mount, uploads on disk |
| PDF Generation | WeasyPrint | >=62.0 | HTML-to-PDF for canvas export |
| Testing (Backend) | pytest + httpx | Latest stable | Async test client |
| Testing (Frontend) | Vitest + React Testing Library | Latest stable | Component + integration tests |
| Containerisation | Docker + Docker Compose | Latest stable | Dev and prod profiles |

### UI & Design

| Aspect | Choice |
|--------|--------|
| CSS Framework | Tailwind CSS 4.x |
| Icon Set | Heroicons (pairs with Tailwind) |
| Font | Barlow (Google Fonts) — weights: Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700 |
| Responsive Breakpoints | Tailwind defaults: sm(640), md(768), lg(1024), xl(1280) |
| Dark Mode | Not in v1 scope |
| Component Pattern | Small, composable React components. No component library — hand-rolled with Tailwind. |

### Style Guide

**Primary Colours:**

| Name | HEX | Usage |
|------|-----|-------|
| Teal | #008AB0 | Primary brand, buttons, links, active states |
| Teal Light | #33A5C4 | Hover states, secondary backgrounds |
| Teal Dark | #006F8E | Active states, emphasis |
| Teal Pale | #B3E0ED | Subtle backgrounds, cards |

**Secondary Colours:**

| Name | HEX | Usage |
|------|-----|-------|
| Green | #80C342 | Success states, "Observed" proof point status |
| Green Light | #9DD066 | Success hover |
| Green Pale | #E8F4D9 | Success backgrounds |
| Blue | #273691 | Headings, deep accents |
| Blue Light | #4A5BAD | Secondary accents |
| Blue Pale | #E8EAF5 | Info backgrounds |
| Navy | #001641 | Dark text, footer |
| Ice Blue | #DDF1F7 | Page backgrounds, light panels |

**Accent Colours:**

| Name | HEX | Usage |
|------|-----|-------|
| Lime | #C1D82F | Highlights, badges |
| Yellow | #F3EA00 | Warnings, "Stalled" proof point status |
| Yellow Dark | #C9BC00 | Warning borders/text |
| Yellow Pale | #FFFBE6 | Warning backgrounds |

**Neutrals:**

| Name | HEX | Usage |
|------|-----|-------|
| Near Black | #1A1A1A | Primary text |
| Dark Gray | #0D0D0D | Headings |
| Medium Gray | #737373 | Secondary text, labels |
| Light Gray | #A6A6A6 | Borders, disabled states |
| Lighter Gray | #DFDFDF | Dividers |
| Lightest Gray | #F5F5F5 | Page backgrounds |

**Typography:**

| Element | Font | Weight | Size |
|---------|------|--------|------|
| H1 | Barlow | Bold 700 | 2rem (32px) |
| H2 | Barlow | SemiBold 600 | 1.5rem (24px) |
| H3 | Barlow | Medium 500 | 1.25rem (20px) |
| Body | Barlow | Regular 400 | 1rem (16px) |
| Small / Labels | Barlow | Medium 500 | 0.875rem (14px) |
| Caption | Barlow | Light 300 | 0.75rem (12px) |

**Proof Point Status Colours:**

| Status | Colour | Background |
|--------|--------|-----------|
| Not Started | #A6A6A6 (Light Gray) | #F5F5F5 |
| In Progress | #008AB0 (Teal) | #B3E0ED |
| Observed | #80C342 (Green) | #E8F4D9 |
| Stalled | #F3EA00 (Yellow) | #FFFBE6 |

**Lifecycle Lane Colours:**

| Lane | Colour | Background |
|------|--------|-----------|
| Build | #008AB0 (Teal) | #B3E0ED |
| Sell | #80C342 (Green) | #E8F4D9 |
| Milk | #273691 (Blue) | #E8EAF5 |
| Reframe | #C1D82F (Lime) | #FFFBE6 |

## Architecture Overview

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
│              │                               │
│  ┌───────────┐  ┌────────────┐              │
│  │File Upload│  │PDF Export  │              │
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

## Features

### 001-auth
**Purpose:** User authentication and role-based access control.
**Success Criteria:** Users can register, log in, receive JWT tokens, and access is restricted by role.
**Inputs:** Email, password, role assignment (admin only).
**Outputs:** JWT access/refresh tokens, user profile.
**Dependencies:** None.
**UI Surface:** Login page, user management page (admin only).

### 002-canvas-management
**Purpose:** CRUD operations for VBUs and their Strategy + Lifecycle Canvases, including all nested entities (theses, proof points, constraints, commitments, file attachments).
**Success Criteria:** A GM can create/edit a canvas with all sections from the Strategy + Lifecycle Canvas template. Data persists correctly. Inline editing works with autosave. Files can be uploaded and attached to proof points or reviews.
**Inputs:** All canvas fields per the data model — context, future state intent, theses, lifecycle implications, proof points, primary constraint, cadence commitments. File uploads.
**Outputs:** Complete canvas data, "currently testing" pointer, proof point statuses, attachment URLs.
**Dependencies:** 001-auth (user ownership, role checks).
**UI Surface:** VBU Page (detail view with all canvas sections).

### 003-portfolio-dashboard
**Purpose:** Aggregated view of all VBUs/products with at-a-glance strategic health indicators. PDF export of individual canvases.
**Success Criteria:** Admin/GL sees all VBUs in a filterable table. Proof point health indicator computed correctly. Click-through to VBU page works. Portfolio notes panel (admin only) persists. Canvas can be exported to PDF.
**Inputs:** Filter criteria (lifecycle lane, GM, proof point health status).
**Outputs:** Table of VBUs with: name, lifecycle lane, 12-24m success sentence, currently testing, next review date, top constraint, proof point health indicator. PDF download.
**Dependencies:** 002-canvas-management (reads canvas data), 001-auth (role-based filtering).
**UI Surface:** Portfolio Dashboard (home page).

### 004-monthly-review
**Purpose:** Guided monthly review wizard that walks GMs through four structured prompts and captures dated review entries with commitments.
**Success Criteria:** GM completes a review wizard answering 4 prompts. Review entry saved with date. Commitments captured. "Currently testing" pointer updated. Review history visible on VBU page.
**Inputs:** Answers to 4 review prompts, 1-3 commitments, "currently testing" selection (thesis or proof point).
**Outputs:** Dated MonthlyReview entry, updated commitments, updated "currently testing" pointer on canvas.
**Dependencies:** 002-canvas-management (reads/updates canvas), 001-auth (GM ownership check).
**UI Surface:** Monthly Review Wizard (separate route), Review History section on VBU Page.

## Data Models

### User
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| email | String(255) | Unique, not null |
| password_hash | String(255) | Not null |
| name | String(255) | Not null |
| role | Enum(admin, gm, viewer) | Not null, default: viewer |
| created_at | Timestamp | Not null, auto |
| updated_at | Timestamp | Not null, auto |

### VBU
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| name | String(255) | Not null |
| gm_id | UUID | FK → User, not null |
| created_at | Timestamp | Not null, auto |
| updated_at | Timestamp | Not null, auto |
| updated_by | UUID | FK → User |

### Canvas
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| vbu_id | UUID | FK → VBU, unique, not null (1:1) |
| product_name | String(255) | Nullable |
| lifecycle_lane | Enum(build, sell, milk, reframe) | Not null |
| success_description | Text | "In this lane, success over 12-24 months means..." |
| future_state_intent | Text | 3-5 year vision statement |
| primary_focus | String(255) | Learning / Replication / Cash & Risk |
| resist_doing | Text | "What we must resist doing" |
| good_discipline | Text | "What good discipline looks like" |
| primary_constraint | Text | Single biggest blocker |
| currently_testing_type | Enum(thesis, proof_point) | Nullable |
| currently_testing_id | UUID | Nullable, polymorphic FK |
| portfolio_notes | Text | Admin-only free text |
| created_at | Timestamp | Not null, auto |
| updated_at | Timestamp | Not null, auto |
| updated_by | UUID | FK → User |

### Thesis
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| canvas_id | UUID | FK → Canvas, not null |
| order | Integer | 1-5, not null |
| text | Text | Not null |
| created_at | Timestamp | Not null, auto |
| updated_at | Timestamp | Not null, auto |

### ProofPoint
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| thesis_id | UUID | FK → Thesis, not null |
| description | Text | Not null, observable signal |
| status | Enum(not_started, in_progress, observed, stalled) | Not null, default: not_started |
| evidence_note | Text | Nullable |
| target_review_month | Date | Nullable |
| created_at | Timestamp | Not null, auto |
| updated_at | Timestamp | Not null, auto |

### MonthlyReview
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| canvas_id | UUID | FK → Canvas, not null |
| review_date | Date | Not null |
| what_moved | Text | "What moved since last month (evidence)?" |
| what_learned | Text | "What did we learn that changes our beliefs?" |
| what_threatens | Text | "What now threatens the next proof point?" |
| currently_testing_type | Enum(thesis, proof_point) | Nullable |
| currently_testing_id | UUID | Nullable |
| created_by | UUID | FK → User, not null |
| created_at | Timestamp | Not null, auto |

### Commitment
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| monthly_review_id | UUID | FK → MonthlyReview, not null |
| text | Text | Not null |
| order | Integer | 1-3, not null |

### Attachment
| Field | Type | Constraints |
|-------|------|------------|
| id | UUID | PK |
| proof_point_id | UUID | FK → ProofPoint, nullable |
| monthly_review_id | UUID | FK → MonthlyReview, nullable |
| filename | String(255) | Not null, original filename |
| storage_path | String(1024) | Not null, path on disk |
| content_type | String(128) | Not null, MIME type |
| size_bytes | Integer | Not null |
| label | String(255) | Nullable, user-provided label |
| uploaded_by | UUID | FK → User, not null |
| created_at | Timestamp | Not null, auto |

**Relationships:**
- User 1:N VBU (as GM)
- VBU 1:1 Canvas
- Canvas 1:N Thesis (max 5, ordered)
- Thesis 1:N ProofPoint
- Canvas 1:N MonthlyReview
- MonthlyReview 1:N Commitment (max 3, ordered)
- Attachment belongs to ProofPoint OR MonthlyReview (one FK set, other null)

## Interfaces

### External API Endpoints

**Auth:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/register | None | Register new user |
| POST | /api/auth/login | None | Login, returns JWT |
| POST | /api/auth/refresh | JWT | Refresh access token |
| GET | /api/auth/me | JWT | Current user profile |

**Users (admin only):**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/users | Admin | List all users |
| PATCH | /api/users/{id} | Admin | Update user role |
| DELETE | /api/users/{id} | Admin | Delete user |

**VBUs:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/vbus | JWT | List VBUs (filtered by role) |
| POST | /api/vbus | Admin | Create VBU |
| GET | /api/vbus/{id} | JWT | Get VBU detail |
| PATCH | /api/vbus/{id} | Admin/GM | Update VBU |
| DELETE | /api/vbus/{id} | Admin | Delete VBU |

**Canvas:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/vbus/{vbu_id}/canvas | JWT | Get canvas for VBU |
| PUT | /api/vbus/{vbu_id}/canvas | GM/Admin | Create or update canvas |
| GET | /api/vbus/{vbu_id}/canvas/pdf | JWT | Export canvas as PDF |

**Theses:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/canvases/{canvas_id}/theses | JWT | List theses |
| POST | /api/canvases/{canvas_id}/theses | GM/Admin | Create thesis |
| PATCH | /api/theses/{id} | GM/Admin | Update thesis |
| DELETE | /api/theses/{id} | GM/Admin | Delete thesis |
| PUT | /api/canvases/{canvas_id}/theses/reorder | GM/Admin | Reorder theses |

**Proof Points:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/theses/{thesis_id}/proof-points | JWT | List proof points |
| POST | /api/theses/{thesis_id}/proof-points | GM/Admin | Create proof point |
| PATCH | /api/proof-points/{id} | GM/Admin | Update proof point |
| DELETE | /api/proof-points/{id} | GM/Admin | Delete proof point |

**Monthly Reviews:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/canvases/{canvas_id}/reviews | JWT | List reviews |
| POST | /api/canvases/{canvas_id}/reviews | GM/Admin | Create review (wizard submit) |
| GET | /api/reviews/{id} | JWT | Get review detail |

**Attachments:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/attachments | GM/Admin | Upload file |
| GET | /api/attachments/{id} | JWT | Download file |
| DELETE | /api/attachments/{id} | GM/Admin | Delete attachment |

**Portfolio:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/portfolio/summary | JWT | Dashboard summary data |
| PATCH | /api/portfolio/notes | Admin | Update portfolio notes |

### API Response Conventions

**Success envelope:**
```json
{
  "data": { ... },
  "meta": { "timestamp": "ISO8601" }
}
```

**List envelope:**
```json
{
  "data": [ ... ],
  "meta": { "total": 42, "page": 1, "per_page": 25, "timestamp": "ISO8601" }
}
```

**Error envelope:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [ { "field": "email", "message": "Already exists" } ]
  }
}
```

### File Upload Constraints

| Constraint | Value |
|-----------|-------|
| Max file size | 10 MB |
| Allowed types | image/png, image/jpeg, image/gif, application/pdf, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| Storage path | /uploads/{vbu_id}/{entity_type}/{uuid}.{ext} |
| Naming | UUID-based on disk, original filename stored in DB |

## Configuration

| Variable | Description | Default (dev) | Required |
|----------|-------------|---------------|----------|
| CANVAS_DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://canvas:canvas@db:5432/canvas | Yes |
| CANVAS_SECRET_KEY | JWT signing key | dev-secret-change-me | Yes |
| CANVAS_ACCESS_TOKEN_EXPIRE_MINUTES | JWT access token TTL | 30 | No |
| CANVAS_REFRESH_TOKEN_EXPIRE_DAYS | JWT refresh token TTL | 7 | No |
| CANVAS_UPLOAD_DIR | File upload directory | /uploads | Yes |
| CANVAS_MAX_UPLOAD_SIZE_MB | Max upload file size | 10 | No |
| CANVAS_CORS_ORIGINS | Allowed CORS origins | http://localhost:5173 | Yes |
| CANVAS_LOG_LEVEL | Logging level | DEBUG | No |
| POSTGRES_USER | PostgreSQL user | canvas | Yes |
| POSTGRES_PASSWORD | PostgreSQL password | canvas | Yes |
| POSTGRES_DB | PostgreSQL database name | canvas | Yes |

## Port Configuration

| Service | Dev Port | Prod Port | Internal Port |
|---------|----------|-----------|---------------|
| Frontend (Vite dev) | 5173 | — | 5173 |
| Frontend (Nginx prod) | — | 80 | 80 |
| Backend (FastAPI) | 8000 | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 | 5432 |

## Auth Flow

1. User submits email + password to `POST /api/auth/login`.
2. Backend verifies credentials, returns `{ access_token, refresh_token, token_type }`.
3. Frontend stores tokens in memory (access) and httpOnly cookie (refresh).
4. All API requests include `Authorization: Bearer {access_token}`.
5. On 401, frontend calls `POST /api/auth/refresh` with refresh token.
6. Backend middleware extracts user from JWT, attaches to request state.
7. Route-level decorators check `role` for authorization.
8. GM routes additionally verify `vbu.gm_id == current_user.id`.

## App Shell & Navigation

```
┌──────────────────────────────────────────────────┐
│  [Logo]  Canvas          [User Menu ▾]           │
├──────────────────────────────────────────────────┤
│  Nav: Dashboard | (VBU name when on detail page) │
├──────────────────────────────────────────────────┤
│                                                  │
│                 Page Content                      │
│                                                  │
└──────────────────────────────────────────────────┘
```

- Top bar: Logo + app name left, user dropdown right (profile, logout).
- Breadcrumb nav below top bar: Dashboard → VBU Name → Monthly Review.
- No sidebar — simple top nav. This is a focused tool, not a platform.
- Mobile: hamburger menu for user dropdown, content stacks vertically.

## Screens

| Route | Screen | Roles | Key Components |
|-------|--------|-------|---------------|
| /login | Login Page | Public | Email/password form |
| / | Portfolio Dashboard | All authenticated | VBU table, filters, portfolio notes (admin) |
| /vbus/:id | VBU Canvas Page | Admin, owning GM, Viewer | Canvas sections, inline edit, proof points, review history |
| /vbus/:id/review/new | Monthly Review Wizard | Admin, owning GM | 4-step wizard form |
| /admin/users | User Management | Admin | User table, role assignment |

## User Flows

**GM Flow:**
1. Login → Portfolio Dashboard (sees own VBUs only)
2. Click VBU → Canvas detail page
3. Edit canvas sections inline (autosave)
4. Add/update theses and proof points
5. Upload evidence files to proof points
6. Click "Start Monthly Review" → Wizard
7. Complete 4 prompts → Set commitments → Select "currently testing" → Submit
8. Return to canvas page, see review in history

**Admin Flow:**
1. Login → Portfolio Dashboard (sees all VBUs)
2. Filter by lane / GM / health status
3. Click VBU → Canvas detail (can edit any)
4. Add portfolio notes
5. Export canvas to PDF
6. Manage users via /admin/users

**Viewer Flow:**
1. Login → Portfolio Dashboard (sees all, read-only)
2. Click VBU → Canvas detail (read-only)
3. Browse review history

## Deployment

### Dev Environment

Docker Compose profile `dev`:
- **frontend**: Vite dev server with HMR, source mounted as volume, port 5173.
- **backend**: FastAPI with `--reload`, source mounted as volume, port 8000.
- **db**: PostgreSQL 18, data persisted in named volume, port 5432 exposed for local tools.
- **uploads**: Named volume mounted to backend at `/uploads`.

```bash
docker compose --profile dev up
```

Startup sequence:
1. `db` starts, healthcheck: `pg_isready`
2. `backend` starts after db healthy, runs Alembic migrations on boot, healthcheck: `GET /api/health`
3. `frontend` starts after backend healthy

### Prod Environment

Docker Compose profile `prod`:
- **frontend**: Multi-stage build — Vite builds static assets, served by Nginx on port 80. Nginx also reverse-proxies `/api` to backend.
- **backend**: Multi-stage build — slim Python image, Uvicorn with multiple workers, no reload, port 8000 (internal only, not exposed).
- **db**: PostgreSQL 18, data persisted in named volume, port NOT exposed externally.
- **uploads**: Named volume mounted to backend at `/uploads`.

```bash
docker compose --profile prod up -d
```

Startup sequence: same as dev (db → backend → frontend).

### Dockerfiles

**backend/Dockerfile:**
- Base: `python:3.12-slim`
- Multi-stage: builder installs deps, final copies venv + app code
- Entrypoint: run Alembic upgrade head, then start Uvicorn
- Dev target: includes dev deps, uses `--reload`
- Prod target: no dev deps, multiple Uvicorn workers

**frontend/Dockerfile:**
- Base: `node:22-alpine`
- Multi-stage: builder runs `npm ci && npm run build`, final copies dist to `nginx:alpine`
- Dev target: just runs `npm run dev` with volume mount
- Prod target: Nginx serves static files, proxies /api

### Health Checks

| Service | Endpoint/Command | Interval | Timeout |
|---------|-----------------|----------|---------|
| db | `pg_isready -U canvas` | 5s | 3s |
| backend | `GET /api/health` returns `{"status": "ok"}` | 10s | 5s |
| frontend (prod) | Nginx returns 200 on `/` | 10s | 5s |

## Seed / Dev Data

On first boot in dev, seed script creates:
- 1 Admin user (admin@canvas.local / admin)
- 2 GM users (gm1@canvas.local / gm1, gm2@canvas.local / gm2)
- 1 Viewer user (viewer@canvas.local / viewer)
- 2 VBUs, each with a canvas, 3 theses, 2 proof points per thesis
- 1 monthly review per canvas with commitments

Seed runs via `python -m canvas.seed` — idempotent, skips if data exists.

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
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── seed.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── dependencies.py
│   │   ├── vbus/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── canvases/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── reviews/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── portfolio/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── attachments/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── pdf/
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── templates/
│   │   │       └── canvas.html
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── vbu.py
│   │   │   ├── canvas.py
│   │   │   ├── thesis.py
│   │   │   ├── proof_point.py
│   │   │   ├── monthly_review.py
│   │   │   ├── commitment.py
│   │   │   └── attachment.py
│   │   └── db.py
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_canvas.py
│       ├── test_reviews.py
│       ├── test_portfolio.py
│       └── test_attachments.py
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── useAuth.ts
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── VBUTable.tsx
│   │   │   └── Filters.tsx
│   │   ├── canvas/
│   │   │   ├── CanvasPage.tsx
│   │   │   ├── ContextSection.tsx
│   │   │   ├── FutureStateSection.tsx
│   │   │   ├── ThesesSection.tsx
│   │   │   ├── ProofPointsSection.tsx
│   │   │   ├── LifecycleSection.tsx
│   │   │   ├── ConstraintSection.tsx
│   │   │   └── CadenceSection.tsx
│   │   ├── reviews/
│   │   │   ├── ReviewWizard.tsx
│   │   │   └── ReviewHistory.tsx
│   │   ├── admin/
│   │   │   └── UserManagement.tsx
│   │   ├── components/
│   │   │   ├── AppShell.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── LaneBadge.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   └── InlineEdit.tsx
│   │   └── styles/
│   │       └── index.css
│   └── tests/
│       ├── setup.ts
│       ├── DashboardPage.test.tsx
│       ├── CanvasPage.test.tsx
│       └── ReviewWizard.test.tsx
└── specs/
```

## Error Handling & Observability

- Backend: structured JSON logging via `structlog`.
- All exceptions caught by FastAPI exception handlers, returned as error envelope.
- Request ID generated per request, included in logs and response headers.
- Dev: log level DEBUG, pretty-printed to stdout.
- Prod: log level INFO, JSON format to stdout (for Docker log collection).

## Testing Strategy

- **Backend unit tests**: pytest with async httpx test client against real PostgreSQL (Docker).
- **Frontend component tests**: Vitest + React Testing Library.
- **Integration tests**: Backend tests hit real DB, no mocks for data layer.
- **Coverage target**: 80% backend, 70% frontend.

## Migration & Rollback

- Alembic manages all schema migrations.
- Migrations auto-generated from SQLAlchemy model changes.
- Backend entrypoint runs `alembic upgrade head` on every boot.
- Rollback: `alembic downgrade -1` manually if needed.

## Open Questions / Assumptions

1. **Assumption:** Single admin user is sufficient for pilot — no admin hierarchy.
2. **Assumption:** "Currently testing" pointer is per-canvas, updated during monthly review only.
3. **Assumption:** Proof point health indicator on dashboard is computed as: if any proof point is "stalled" → At Risk; if all are "not_started" → Not Started; if any "observed" and none "stalled" → On Track; else → In Progress.
4. **Open:** Should GMs be able to see each other's canvases read-only, or is it strictly isolated? Current spec: strictly isolated.

## Ubiquitous Language

| Term | Definition | NOT This |
|------|-----------|----------|
| Canvas | The single living strategy document per VBU/product containing all sections | Strategy doc, plan, roadmap |
| VBU | Virtual Business Unit — the organisational entity that owns a canvas | Company, team, department |
| Thesis | A strategic hypothesis about what must become true (12-36 months). Phrased as a "new normal", not a project. Max 5 per canvas. | Initiative, project, goal, KPI |
| Proof Point | An observable signal (not an activity) that a thesis is strengthening or weakening. 3-6 month horizon. | Task, milestone, deliverable, KPI |
| Lifecycle Lane | One of Build / Sell / Milk / Reframe — determines the behavioural discipline for the VBU | Stage, phase, maturity |
| Monthly Review | A structured check-in answering 4 prompts, capturing evidence and updating commitments | Status update, standup, retrospective |
| Currently Testing | The thesis or proof point that is the primary focus for the next review period | Priority, OKR, sprint goal |
| Primary Constraint | The single biggest blocker preventing the next proof point from appearing | Risk register, issue list |
| Commitment | 1-3 specific actions promised before the next monthly review | Task, action item, to-do |
| Portfolio Dashboard | The aggregated view of all VBUs showing strategic health at a glance | Report, analytics, homepage |
| Evidence | Observable real-world signals that a thesis is proving true or false | Activity, output, deliverable |

## Glossary

| Term | Definition |
|------|-----------|
| GM | General Manager — the person responsible for a VBU's strategy |
| GL | Group Leader — the admin/portfolio owner who oversees all VBUs |
| JWT | JSON Web Token — used for stateless authentication |
| SPA | Single Page Application — the React frontend architecture |
| HMR | Hot Module Replacement — Vite's live reload during development |
