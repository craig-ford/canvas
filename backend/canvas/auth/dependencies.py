from typing import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User, UserRole
from canvas.auth.service import AuthService
from canvas.db import get_db_session
from canvas.config import Settings

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Extract and validate user from JWT token."""
    token = credentials.credentials
    
    # Verify token using AuthService
    payload = await auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Extract user ID from token payload
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    user = await auth_service.get_user_by_id(user_id, db)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def require_role(*roles) -> Callable[[User], User]:
    """Create dependency that requires user to have one of specified roles."""
    # Flatten if a list was passed as single argument
    flat_roles = roles[0] if len(roles) == 1 and isinstance(roles[0], list) else list(roles)
    # Normalize: accept both UserRole enums and string values
    normalized = set()
    for r in flat_roles:
        if isinstance(r, UserRole):
            normalized.add(r)
        elif isinstance(r, str):
            normalized.add(UserRole(r))
        else:
            normalized.add(r)

    def role_checker(user: User = Depends(get_current_user)) -> User:
        """Check if current user has required role."""
        if user.role not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker

async def verify_csrf(request: Request) -> None:
    """Verify CSRF protection by checking Origin header for state-changing requests."""
    settings = Settings()
    
    # Get Origin header
    origin = request.headers.get("origin")
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Origin header"
        )
    
    # Check if origin is in allowed CORS origins
    if origin not in settings.cors_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Origin header"
        )
    
    return None