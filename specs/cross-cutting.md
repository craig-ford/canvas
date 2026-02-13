# Cross-Cutting Contracts

## Shared Service Interfaces

### Auth Dependency (owned by 001-auth)
```python
async def get_current_user(credentials, db) -> User
def require_role(*roles) -> Callable  # Returns dependency that checks user.role
```
Consumed by: 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review

### Response Helpers (owned by 001A-infrastructure)
```python
def success_response(data, status_code=200) -> dict
def list_response(data, total, page=1, per_page=25) -> dict
```
Consumed by: all features

### File Storage Service (owned by 002-canvas-management)
```python
class AttachmentService:
    async def upload(file: UploadFile, vbu_id: UUID, entity_type: str, uploaded_by: UUID) -> Attachment
    async def download(attachment_id: UUID) -> FileResponse
    async def delete(attachment_id: UUID) -> None
```
Consumed by: 002-canvas-management, 004-monthly-review

### PDF Export Service (owned by 003-portfolio-dashboard)
```python
class PDFService:
    async def export_canvas(canvas_id: UUID) -> bytes
```
Consumed by: 003-portfolio-dashboard

## Environment Variables

| Variable | Purpose | Required | Default | Owning Spec |
|----------|---------|----------|---------|-------------|
| CANVAS_DATABASE_URL | PostgreSQL connection string | Yes | postgresql+asyncpg://canvas:canvas@db:5432/canvas | 001A-infrastructure |
| CANVAS_SECRET_KEY | JWT signing key | Yes | dev-secret-change-me | 001-auth |
| CANVAS_ACCESS_TOKEN_EXPIRE_MINUTES | JWT access token TTL | No | 30 | 001-auth |
| CANVAS_REFRESH_TOKEN_EXPIRE_DAYS | JWT refresh token TTL | No | 7 | 001-auth |
| CANVAS_UPLOAD_DIR | File upload directory | Yes | /uploads | 002-canvas-management |
| CANVAS_MAX_UPLOAD_SIZE_MB | Max upload file size | No | 10 | 002-canvas-management |
| CANVAS_CORS_ORIGINS | Allowed CORS origins | Yes | http://localhost:5173 | 001A-infrastructure |
| CANVAS_LOG_LEVEL | Logging level | No | DEBUG | 001A-infrastructure |
| POSTGRES_USER | PostgreSQL user | Yes | canvas | 001A-infrastructure |
| POSTGRES_PASSWORD | PostgreSQL password | Yes | canvas | 001A-infrastructure |
| POSTGRES_DB | PostgreSQL database name | Yes | canvas | 001A-infrastructure |

## External Dependencies

| Service | Purpose | Failure Mode | Consuming Features |
|---------|---------|--------------|-------------------|
| Google Fonts CDN | Barlow font loading | Graceful degradation to system font | 001A-infrastructure (frontend) |

No external API integrations in v1.

## Shared Infrastructure

### Logging
- Backend: `structlog` with JSON structured logging
- Request ID generated per request, included in logs and `X-Request-ID` response header
- Dev: DEBUG level, pretty-printed to stdout
- Prod: INFO level, JSON format to stdout

### Error Handling
- All exceptions caught by FastAPI exception handlers
- Returned as standard error envelope: `{ "error": { "code", "message", "details" } }`
- No sensitive information in error responses

### Database
- Async SQLAlchemy with asyncpg driver
- Connection pool managed by engine
- Alembic migrations auto-generated from model changes
- Backend entrypoint runs `alembic upgrade head` on every boot

### File Storage
- Local filesystem at `CANVAS_UPLOAD_DIR` (Docker volume)
- Path pattern: `/uploads/{vbu_id}/{entity_type}/{uuid}.{ext}`
- Max 10MB per file
- Allowed types: image/png, image/jpeg, image/gif, application/pdf, text/csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
