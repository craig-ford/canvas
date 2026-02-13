# Feature 001-auth: User Authentication & Role-Based Access Control

## Overview

Provides user authentication via email/password with JWT tokens and role-based access control for the Canvas application. Supports three roles: admin (full access), gm (own VBUs only), and viewer (read-only). Includes user management capabilities for admins.

## Functional Requirements

### FR-001: User Registration
**Acceptance Criteria:**
- Admin can register new users via POST /api/auth/register
- Email must be unique across all users
- Password is hashed using bcrypt before storage
- Default role is 'viewer' unless specified
- Returns user profile without password hash

### FR-002: User Login
**Acceptance Criteria:**
- Users authenticate via POST /api/auth/login with email/password
- Returns JWT access token (30min TTL) and refresh token (7 day TTL)
- Access token stored in memory, refresh token in httpOnly cookie
- Invalid credentials return 401 with error message

### FR-003: Token Refresh
**Acceptance Criteria:**
- POST /api/auth/refresh accepts refresh token from httpOnly cookie
- Returns new access token if refresh token is valid
- Expired/invalid refresh tokens return 401
- New access token has full 30min TTL

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

### FR-006: User Management (Admin Only)
**Acceptance Criteria:**
- GET /api/users lists all users (admin only)
- PATCH /api/users/{id} updates user role (admin only)
- DELETE /api/users/{id} removes user (admin only)
- Non-admin access returns 403

## Technical Requirements

### TR-001: JWT Implementation
- Use python-jose for JWT encoding/decoding
- Access tokens expire in 30 minutes (configurable)
- Refresh tokens expire in 7 days (configurable)
- Tokens signed with CANVAS_SECRET_KEY

### TR-002: Password Security
- Use passlib with bcrypt for password hashing
- Minimum password length: 8 characters
- Store only bcrypt hash, never plaintext

### TR-003: Database Schema
- User model with UUID primary key
- Email unique constraint with index
- Role enum: admin, gm, viewer
- Timestamp tracking (created_at, updated_at)

### TR-004: Auth Dependencies
- Provide get_current_user dependency for route protection
- Provide require_role(*roles) dependency factory
- Extract user from JWT and attach to request.state.user

## API Endpoints

### POST /api/auth/register
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

### POST /api/auth/login
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

### POST /api/auth/refresh
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

### GET /api/auth/me
**Headers:** Authorization: Bearer {access_token}

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
**Headers:** Authorization: Bearer {access_token}

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

### DELETE /api/users/{id}
**Auth:** Admin only

**Response (204):** No content

## Data Models

### User
```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)

class UserRole(str, Enum):
    ADMIN = "admin"
    GM = "gm"
    VIEWER = "viewer"
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
```

### UserService
```python
class UserService:
    async def list_users(self, db: AsyncSession) -> list[User]
    async def update_user_role(self, user_id: UUID, role: UserRole, db: AsyncSession) -> User
    async def delete_user(self, user_id: UUID, db: AsyncSession) -> None
```

## Auth Dependencies

### get_current_user
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
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

### require_role
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
```
┌─────────────────────────────────────────────┐
│                                             │
│              [Canvas Logo]                  │
│                                             │
│         Strategy Portfolio Dashboard        │
│                                             │
│    ┌─────────────────────────────────────┐  │
│    │  Email                              │  │
│    │  [user@canvas.local            ]    │  │
│    │                                     │  │
│    │  Password                           │  │
│    │  [••••••••••••••••••••••••••••]    │  │
│    │                                     │  │
│    │           [Sign In]                 │  │
│    │                                     │  │
│    │  □ Remember me                      │  │
│    └─────────────────────────────────────┘  │
│                                             │
│         Forgot password? Contact admin      │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Centered login form with Canvas branding
- Email and password fields with validation
- Sign In button (teal #008AB0)
- Error messages displayed above form
- Responsive design for mobile

### User Management Page (Admin Only)
```
┌─────────────────────────────────────────────────────────────────┐
│  User Management                                    [+ Add User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Name          │ Email              │ Role   │ Actions      │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Admin User    │ admin@canvas.local │ Admin  │ [Edit] [Del] │ │
│  │ GM One        │ gm1@canvas.local   │ GM     │ [Edit] [Del] │ │
│  │ GM Two        │ gm2@canvas.local   │ GM     │ [Edit] [Del] │ │
│  │ Viewer User   │ viewer@canvas.local│ Viewer │ [Edit] [Del] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Table of all users with name, email, role
- Add User button opens modal form
- Edit button opens role selection dropdown
- Delete button with confirmation dialog
- Role badges with appropriate colors

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

## Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| CANVAS_SECRET_KEY | JWT signing key | Yes | dev-secret-change-me |
| CANVAS_ACCESS_TOKEN_EXPIRE_MINUTES | Access token TTL | No | 30 |
| CANVAS_REFRESH_TOKEN_EXPIRE_DAYS | Refresh token TTL | No | 7 |

## Error Handling

| Scenario | HTTP Status | Error Code | Message |
|----------|-------------|------------|---------|
| Invalid credentials | 401 | UNAUTHORIZED | Invalid email or password |
| Expired token | 401 | UNAUTHORIZED | Token has expired |
| Invalid token | 401 | UNAUTHORIZED | Invalid token |
| Insufficient role | 403 | FORBIDDEN | Insufficient permissions |
| Email already exists | 409 | CONFLICT | Email already registered |
| User not found | 404 | NOT_FOUND | User not found |

## Security Considerations

- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens include expiration and issuer claims
- Refresh tokens stored in httpOnly cookies
- Access tokens stored in memory only
- No sensitive data in JWT payload
- Rate limiting on auth endpoints [NEEDS CLARIFICATION: Rate limiting implementation]

## Testing Strategy

### Backend Tests
- Unit tests for AuthService methods
- Integration tests for auth endpoints
- JWT token validation tests
- Password hashing/verification tests
- Role-based access control tests

### Frontend Tests
- useAuth hook behavior tests
- Login form validation tests
- Token refresh flow tests
- Protected route access tests

## Dependencies

- **Upstream:** 001A-infrastructure (database, response helpers)
- **Downstream:** 002-canvas-management, 003-portfolio-dashboard, 004-monthly-review

## Seed Data

Development environment includes:
- admin@canvas.local / admin (role: admin)
- gm1@canvas.local / gm1 (role: gm)
- gm2@canvas.local / gm2 (role: gm)
- viewer@canvas.local / viewer (role: viewer)