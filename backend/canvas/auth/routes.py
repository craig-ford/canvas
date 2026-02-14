from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from canvas.auth.service import AuthService
from canvas.auth.user_service import UserService
from canvas.auth.dependencies import get_current_user, require_role
from canvas.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from canvas.models.user import User, UserRole
from canvas.db import get_db_session
from canvas import success_response, list_response

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()
user_service = UserService()

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
    response: Response,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Authenticate user and return tokens."""
    user = await auth_service.authenticate_user(
        email=credentials.email,
        password=credentials.password,
        db=db
    )
    
    if not user:
        await auth_service.increment_failed_attempts(credentials.email, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    await auth_service.reset_failed_attempts(user, db)
    
    access_token = await auth_service.create_access_token(user)
    refresh_token = await auth_service.create_refresh_token(user)
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active
    )
    
    return success_response({
        "access_token": access_token,
        "refresh_token": refresh_token,
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
        is_active=current_user.is_active
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
            is_active=user.is_active
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