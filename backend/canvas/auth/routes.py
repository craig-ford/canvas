import threading
from uuid import UUID
from typing import Dict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from canvas.auth.service import AuthService
from canvas.auth.user_service import UserService
from canvas.auth.dependencies import get_current_user, require_role
from canvas.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse, ResetPasswordRequest
from canvas.models.user import User, UserRole
from canvas.db import get_db_session
from canvas.config import Settings
from canvas import success_response, list_response

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()
user_service = UserService()
settings = Settings()

# Simple in-memory rate limiting (for production, use Redis)
# NOTE: This in-memory store is not persistent across server restarts.
# For multi-instance deployments, use Redis-backed rate limiting.
rate_limit_store: Dict[str, Dict[str, datetime]] = {}
rate_limit_lock = threading.Lock()

def check_rate_limit(key: str, limit: int = 5, window_minutes: int = 15) -> None:
    """Check rate limit for given key"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)
    
    with rate_limit_lock:
        if key not in rate_limit_store:
            rate_limit_store[key] = {}
        
        # Clean old entries
        rate_limit_store[key] = {
            k: v for k, v in rate_limit_store[key].items() 
            if v > window_start
        }
        
        # Check limit
        if len(rate_limit_store[key]) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        rate_limit_store[key][str(now)] = now

@router.post("/register", response_model=dict, status_code=201)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> dict:
    """Register new user (admin only)."""
    try:
        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            role=user_data.role,
            db=db
        )
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active
        )
        return success_response(user_response.model_dump())
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

@router.post("/login", response_model=dict)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Authenticate user and return tokens."""
    # Rate limit by IP address
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"login:{client_ip}", limit=5, window_minutes=15)
    
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
        db=db
    )
    
    if not user:
        await auth_service.increment_failed_attempts(credentials.email, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    await auth_service.reset_failed_attempts(user, db)
    
    access_token = await auth_service.create_access_token(user)
    refresh_token = await auth_service.create_refresh_token(user)
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        must_reset_password=user.must_reset_password
    )
    
    return success_response({
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response.model_dump()
    })

@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Refresh access token using refresh token from cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    payload = await auth_service.verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = UUID(payload["sub"])
    user = await auth_service.get_user_by_id(user_id, db)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = await auth_service.create_access_token(user)
    
    return success_response({
        "access_token": access_token,
        "token_type": "bearer"
    })


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Clear refresh token cookie."""
    response.delete_cookie(key="refresh_token", httponly=True, secure=settings.environment == "production", samesite="strict")
    return success_response({"message": "Logged out"})

@router.get("/me", response_model=dict)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get current user profile."""
    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        must_reset_password=current_user.must_reset_password
    )
    return success_response(user_response.model_dump())

@router.get("/users", response_model=dict)
async def list_users(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> dict:
    """List all users (admin only)."""
    users = await user_service.list_users(db)
    user_responses = [
        UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            must_reset_password=user.must_reset_password
        ).model_dump()
        for user in users
    ]
    return list_response(user_responses, len(user_responses))

@router.patch("/users/{user_id}", response_model=dict)
async def update_user_role(
    user_id: str,
    role_data: dict,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> dict:
    """Update user role (admin only)."""
    try:
        user_uuid = UUID(user_id)
        role = UserRole(role_data["role"])
        
        user = await user_service.update_user_role(user_uuid, role, db)
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active
        )
        return success_response(user_response.model_dump())
    except ValueError as e:
        if "User" in str(e) and "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user ID or role"
        )

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> None:
    """Delete user (admin only)."""
    try:
        user_uuid = UUID(user_id)
        
        # Prevent self-deletion
        if user_uuid == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete own account"
            )
        
        await user_service.delete_user(user_uuid, db)
    except ValueError as e:
        if "User" in str(e) and "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user ID"
        )


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Reset password for current user. If must_reset_password is true, current_password is optional."""
    if not current_user.must_reset_password:
        if not body.current_password or not auth_service._verify_password(body.current_password, current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    current_user.password_hash = auth_service._hash_password(body.new_password)
    current_user.must_reset_password = False
    await db.commit()
    return success_response({"message": "Password updated"})


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> dict:
    """Admin generates a temporary password for a user."""
    import secrets
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid user ID")
    user = await auth_service.get_user_by_id(uid, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot reset admin password")
    temp_password = secrets.token_urlsafe(9)  # ~12 chars
    user.password_hash = auth_service._hash_password(temp_password)
    user.must_reset_password = True
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()
    return success_response({"temporary_password": temp_password})
