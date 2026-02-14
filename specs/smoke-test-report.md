# Smoke Test Report

**Date:** 2026-02-14T13:25:00-08:00
**Result:** PASS

## Discovered Configuration
| Service | Port | Health Endpoint | Source |
|---------|------|-----------------|--------|
| PostgreSQL | 5432 | pg_isready | docker-compose.yml |
| Backend (FastAPI) | 8001→8000 | /api/health | docker-compose.yml |
| Frontend (Vite dev) | 5173 | / | docker-compose.yml (dev profile) |

## Validation Checks
| Check | Command | Result |
|-------|---------|--------|
| Backend import | `python -c "from canvas.main import create_app"` | PASS |
| Frontend build | `npm run build` | PASS |
| Silent fallback scan | `rg "AVAILABLE.*=.*False"` | PASS (none found) |
| Swallowed exceptions scan | `rg "except.*:" -A 2` | PASS (none found) |

## Health Checks
| Service | URL | Status |
|---------|-----|--------|
| Backend health | http://localhost:8001/api/health | 200 OK `{"status":"ok"}` |
| Backend docs | http://localhost:8001/docs | 200 OK |
| Auth endpoint | http://localhost:8001/api/auth/me | 401 Unauthorized (correct) |
| VBU endpoint | http://localhost:8001/api/vbus | 401 Unauthorized (correct) |

## Fixes Applied During Smoke Test
1. **Router wiring**: All 8 feature routers were not registered in `main.py` — added `app.include_router()` for auth, vbu, canvas, thesis, proof_point, attachment, portfolio, reviews
2. **Exception handlers**: `http_exception_handler` and `general_exception_handler` returned `dict` instead of `JSONResponse` — fixed to return proper `JSONResponse` with status codes
3. **Pydantic v2 compatibility**: `reviews/schemas.py` used deprecated `regex` (→`pattern`), `min_items`/`max_items` (→`min_length`/`max_length`), `@validator` (→`@field_validator`), `class Config` (→`model_config`)
4. **Frontend import**: `FileUploadStep.tsx` used named import `{ FileUpload }` but `FileUpload.tsx` uses default export — fixed to `import FileUpload from ...`
5. **Dockerfile deps**: Added `pydantic[email]`, `python-multipart`, `weasyprint`, `jinja2` and system libraries (`libglib2.0-0t64`, `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf-2.0-0`)

## API Routes Registered (26 total)
- `/api/health` — Health check
- `/api/auth/*` — Authentication (login, register, refresh, me, users)
- `/api/vbus/*` — VBU CRUD + canvas + PDF export
- `/api/canvases/*/theses/*` — Thesis management
- `/api/proof-points/*` — Proof point management
- `/api/attachments/*` — File attachments
- `/api/portfolio/*` — Portfolio dashboard (summary, notes)
- `/api/canvases/*/reviews/*` — Monthly reviews
