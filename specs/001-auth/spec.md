# Feature 001-auth: User Authentication & Role-Based Access Control

## Overview

Provides user authentication via email/password with JWT tokens and role-based access control for the Canvas application. Supports three roles: admin (full access), gm (own VBUs only), and viewer (read-only). Includes user management capabilities for admins.

## Functional Requirements

### FR-001: User Registration
**Acceptance Criteria:**
- Admin can register new users via POST /api/auth/register
- Email must be unique across all users (case-insensitive)
- Password is hashed using bcrypt before storage with cost factor 12
- Default role is 'viewer' unless specified
- Returns user profile without password hash
- Only admins can create admin users

### FR-002: User Login
**Acceptance Criteria:**
- Users authenticate via POST /api/auth/login with email/password
- Returns JWT access token (30min TTL) and refresh token (7 day TTL)
- Access token stored in memory, refresh token in httpOnly cookie
- Invalid credentials return 401 with generic error message
- Rate limited: 5 attempts per IP per 15 minutes
- Account lockout after 5 failed attempts (15 minute cooldown)

### FR-003: Token Refresh
**Acceptance Criteria:**
- POST /api/auth/refresh accepts refresh token from httpOnly cookie
- Returns new access token if refresh token is valid
- Expired/invalid refresh tokens return 401
- New access token has full 30min TTL
- Rate limited: 10 requests per user per minute

### FR-004: Current User Profile
**Acceptance Criteria:**
- GET /api/auth/me returns current user profile
- Requires valid JWT access token
- Returns user id, email, name, role, timestamps
- Does not return password hash

### FR-005: Role-Based Authorization
**Acceptance Criteria:**
- Admin: Full access to all resources
- GM: Access to own VBUs only, cannot manage users
- Viewer: Read-only access to all resources
- Unauthorized access returns 403 with error message
- Database queries automatically filtered by ownership for GMs

### FR-006: User Management (Admin Only)
**Acceptance Criteria:**
- GET /api/users lists all users (admin only)
- PATCH /api/users/{id} updates user role (admin only)
- DELETE /api/users/{id} removes user (admin only)
- Non-admin access returns 403
- Cannot delete own account

## Technical Requirements

### TR-001: JWT Implementation
- Use python-jose for JWT encoding/decoding
- Access tokens expire in 30 minutes (configurable via CANVAS_ACCESS_TOKEN_EXPIRE_MINUTES)
- Refresh tokens expire in 7 days (configurable via CANVAS_REFRESH_TOKEN_EXPIRE_DAYS)
- Tokens signed with CANVAS_SECRET_KEY
- Include user role in access token payload

### TR-002: Password Security
- Use passlib with bcrypt for password hashing
- Minimum password length: 8 characters, maximum 128 characters
- Bcrypt cost factor 12 (configurable)
- Store only bcrypt hash, never plaintext
- No character composition requirements (NIST guidelines)

### TR-003: Database Schema
- User model with UUID primary key
- Email unique constraint with index (case-insensitive)
- Role enum: admin, gm, viewer
- Timestamp tracking (created_at, updated_at)
- Additional fields: is_active, last_login_at, failed_login_attempts, locked_until

### TR-004: Auth Dependencies
- Provide get_current_user dependency for route protection
- Provide require_role(*roles) dependency factory
- Extract user from JWT and attach to request.state.user
- Maintain exact interface signatures from cross-cutting.md

### TR-005: Rate Limiting
- Login endpoint: 5 attempts per IP per 15 minutes
- Registration: 2 requests per admin per minute
- Token refresh: 10 requests per user per minute
- Progressive delays on failed attempts (1s, 2s, 4s, 8s, 16s)
- Redis-based sliding window implementation

### TR-006: Security Headers
- Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options
- Content-Security-Policy, X-XSS-Protection
- CORS configuration for allowed origins

## API Endpoints

### POST /api/auth/register
**Auth:** Admin only
**Request:**
```json
{
  "email": "user@canvas.local",
  "password": "password123",
  "name": "User Name",
  "role": "gm"
}
```

**Response (201):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@canvas.local",
    "name": "User Name",
    "role": "gm",
    "created_at": "2026-02-13T14:00:00Z",
    "updated_at": "2026-02-13T14:00:00Z"
  },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

**Errors:**
- 422 VALIDATION_ERROR: Invalid email format, password too short, invalid role
- 409 CONFLICT: Email already registered
- 403 FORBIDDEN: Non-admin creating admin user

### POST /api/auth/login
**Rate Limit:** 5 requests per IP per 15 minutes
**Request:**
```json
{
  "email": "user@canvas.local",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@canvas.local",
      "name": "User Name",
      "role": "gm"
    }
  },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

**Errors:**
- 401 UNAUTHORIZED: Invalid email or password (generic message)
- 429 TOO_MANY_REQUESTS: Rate limit exceeded
- 422 VALIDATION_ERROR: Missing required fields

### POST /api/auth/refresh
**Rate Limit:** 10 requests per user per minute
**Request:** Refresh token in httpOnly cookie

**Response (200):**
```json
{
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer"
  },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

**Errors:**
- 401 UNAUTHORIZED: Missing, invalid, or expired refresh token

### GET /api/auth/me
**Auth:** Bearer token required
**Response (200):**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@canvas.local",
    "name": "User Name",
    "role": "gm",
    "created_at": "2026-02-13T14:00:00Z",
    "updated_at": "2026-02-13T14:00:00Z"
  },
  "meta": { "timestamp": "2026-02-13T14:00:00Z" }
}
```

### GET /api/users
**Auth:** Admin only
**Response (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "email": "admin@canvas.local",
      "name": "Admin User",
      "role": "admin",
      "created_at": "2026-02-13T14:00:00Z",
      "updated_at": "2026-02-13T14:00:00Z"
    }
  ],
  "meta": { "total": 1, "timestamp": "2026-02-13T14:00:00Z" }
}
```

### PATCH /api/users/{id}
**Auth:** Admin only
**Request:**
```json
{
  "role": "gm"
}
```

**Response (200):** Updated user object

### DELETE /api/users/{id}
**Auth:** Admin only
**Response (204):** No content
**Errors:**
- 409 CONFLICT: Cannot delete own account

## Data Models

### User
```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum('admin','gm','viewer', name='user_role_enum'), nullable=False, server_default='viewer')
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)

class UserRole(str, Enum):
    ADMIN = "admin"
    GM = "gm"
    VIEWER = "viewer"
```

### Database Constraints
- Email: Unique, case-insensitive, RFC 5322 format validation
- Password hash: Minimum 60 characters (bcrypt requirement)
- Name: Non-empty after trimming whitespace
- Failed attempts: Non-negative integer
- Indexes: email (unique), role, is_active, last_login_at

### Migration Strategy
```sql
CREATE TYPE user_role_enum AS ENUM ('admin', 'gm', 'viewer');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
CREATE INDEX ix_users_role ON users (role);
CREATE INDEX ix_users_is_active ON users (is_active);
```

## Service Layer

### AuthService
```python
class AuthService:
    async def register_user(self, user_data: UserCreate, db: AsyncSession) -> User
    async def authenticate_user(self, email: str, password: str, db: AsyncSession) -> User | None
    async def create_access_token(self, user: User) -> str
    async def create_refresh_token(self, user: User) -> str
    async def verify_token(self, token: str) -> dict | None
    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> User | None
    async def increment_failed_attempts(self, email: str, db: AsyncSession) -> None
    async def reset_failed_attempts(self, user: User, db: AsyncSession) -> None
    async def is_account_locked(self, user: User) -> bool
```

### UserService
```python
class UserService:
    async def list_users(self, db: AsyncSession) -> list[User]
    async def update_user_role(self, user_id: UUID, role: UserRole, db: AsyncSession) -> User
    async def delete_user(self, user_id: UUID, db: AsyncSession) -> None
    async def get_user_by_email(self, email: str, db: AsyncSession) -> User | None
```

## Auth Dependencies

### get_current_user (Cross-cutting Contract)
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await auth_service.get_user_by_id(payload["sub"], db)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

### require_role (Cross-cutting Contract)
```python
def require_role(*roles: UserRole) -> Callable:
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker
```

## UI Components

### Login Page
**Layout:** Centered form with Canvas branding
**States:** Default, loading, error, field validation
**Responsive:** Mobile-first design with breakpoints at 768px, 1024px

**Features:**
- Email and password fields with real-time validation on blur
- Sign In button with loading spinner
- Remember me checkbox
- Error messages displayed above form
- Keyboard navigation support (Tab order, Enter to submit)
- ARIA labels for screen readers

**Validation:**
- Email: Valid format, required
- Password: Required, minimum 8 characters
- Generic error: "Invalid email or password"

### User Management Page (Admin Only)
**Layout:** Table with search and filters
**Features:**
- Add User button opens modal form
- Search input filters table in real-time
- Role filter dropdown (All, Admin, GM, Viewer)
- Sortable columns (Name, Email, Role)
- Edit/Delete actions per row
- Pagination for large user lists

**States:**
- Loading: Skeleton table
- Empty: "No users found" with call-to-action
- Error: Retry button with error message

### Modals
**Add User Modal:**
- Name, Email, Password, Role fields
- Form validation with inline error messages
- Create/Cancel buttons

**Delete Confirmation:**
- User details display
- Warning about irreversible action
- Delete/Cancel buttons

## Security Implementation

### Authentication Flow
1. User submits credentials to POST /api/auth/login
2. Backend verifies via bcrypt, checks account lock status
3. Returns access token (memory) + refresh token (httpOnly cookie)
4. Frontend includes Bearer token in Authorization header
5. Middleware extracts user from JWT, attaches to request.state.user
6. On 401, frontend auto-refreshes token or redirects to login

### Authorization Matrix
| Resource | Admin | GM (own) | GM (other) | Viewer |
|----------|-------|----------|------------|--------|
| VBU list | All | Own only | — | All (read) |
| Canvas read | All | Own | — | All |
| Canvas write | All | Own | — | — |
| User management | ✅ | — | — | — |

### Rate Limiting Implementation
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/15minutes")
async def login(request: Request, ...):
    pass
```

### Security Headers
```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Audit Logging
**Events Logged:**
- User login/logout (user_id, ip_address, timestamp)
- Failed login attempts (email, ip_address, reason)
- User registration (admin_id, new_user_id, email)
- Role changes (admin_id, target_user_id, old_role, new_role)
- User deletion (admin_id, deleted_user_id, email)

**Log Format:**
```json
{
  "event": "user_login",
  "user_id": "uuid",
  "email": "u***@d***.com",
  "ip_address": "192.168.1.100",
  "timestamp": "2026-02-13T14:00:00Z",
  "request_id": "req-uuid"
}
```

**Retention:** 90 days for login events, 1 year for admin actions

## Frontend Implementation

### useAuth Hook
```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const useAuth = (): AuthState & AuthActions
```

### API Client Setup
```typescript
// Axios interceptors for token management
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await refreshToken();
        return api.request(error.config);
      } catch {
        logout();
      }
    }
    return Promise.reject(error);
  }
);
```

### Accessibility Features
- **Keyboard Navigation:** Tab order, Enter/Space activation, Escape for modals
- **Screen Reader Support:** ARIA labels, live regions for errors/loading
- **Focus Management:** Trapped in modals, returns to trigger on close
- **Color Contrast:** WCAG AA compliance (4.5:1 minimum)
- **Form Validation:** Real-time feedback with clear error messages

## Testing Strategy

### Unit Tests
- AuthService methods (registration, authentication, token creation/verification)
- UserService CRUD operations
- Password hashing/verification
- JWT token validation
- Role-based access control logic
- Rate limiting functionality

### Integration Tests
- Full authentication flow (register → login → profile access)
- Token refresh mechanism
- Cross-role authorization on protected endpoints
- User management workflows (admin operations)
- Error handling for invalid inputs/expired tokens

### Edge Cases Tested
- Duplicate email registration → 409 CONFLICT
- Login with non-existent email → 401 with generic message
- Token expiration handling → 401 with refresh attempt
- GM accessing other GM's resources → 403 FORBIDDEN
- Account lockout after failed attempts → 429 with retry-after
- Password validation (< 8 chars, empty) → 422 VALIDATION_ERROR

### Test Data Requirements
- Seed users with each role (admin/gm/viewer)
- Known password hashes for login tests
- Expired tokens for expiration testing
- Multiple GMs with separate VBUs for cross-access tests

### Performance Benchmarks
- User login: < 200ms
- Token refresh: < 100ms
- User registration: < 300ms
- Role check middleware: < 10ms per request

## Environment Variables

| Variable | Purpose | Required | Default | Notes |
|----------|---------|----------|---------|-------|
| CANVAS_SECRET_KEY | JWT signing key | Yes | dev-secret-change-me | 256-bit minimum |
| CANVAS_ACCESS_TOKEN_EXPIRE_MINUTES | Access token TTL | No | 30 | Minutes |
| CANVAS_REFRESH_TOKEN_EXPIRE_DAYS | Refresh token TTL | No | 7 | Days |

## Error Handling

| Scenario | HTTP Status | Error Code | Message |
|----------|-------------|------------|---------|
| Invalid credentials | 401 | UNAUTHORIZED | Invalid email or password |
| Expired token | 401 | UNAUTHORIZED | Token has expired |
| Invalid token | 401 | UNAUTHORIZED | Invalid token |
| Insufficient role | 403 | FORBIDDEN | Insufficient permissions |
| Email already exists | 409 | CONFLICT | Email already registered |
| User not found | 404 | NOT_FOUND | User not found |
| Rate limit exceeded | 429 | TOO_MANY_REQUESTS | Too many requests |
| Account locked | 429 | TOO_MANY_REQUESTS | Account temporarily locked |

## Dependencies

- **Upstream:** 001A-infrastructure (database, response helpers)
- **Downstream:** 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review

## Seed Data

Development environment includes:
- admin@canvas.local / admin (role: admin)
- gm1@canvas.local / gm1 (role: gm)
- gm2@canvas.local / gm2 (role: gm)
- viewer@canvas.local / viewer (role: viewer)

All passwords bcrypt hashed with cost factor 12.