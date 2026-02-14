from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from canvas.models.user import User, UserRole
from canvas.config import Settings

class AuthService:
    """Authentication service handling user registration, login, and JWT tokens."""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        self.secret_key = self.settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.refresh_token_expire_days
    
    async def register_user(self, email: str, password: str, name: str, role: str, db: AsyncSession) -> User:
        """Register a new user with hashed password."""
        password_hash = self._hash_password(password)
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            name=name,
            role=UserRole(role)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def authenticate_user(self, email: str, password: str, db: AsyncSession) -> Optional[User]:
        """Authenticate user credentials, return User if valid, None if invalid."""
        stmt = select(User).where(User.email == email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not self._verify_password(password, user.password_hash):
            return None
        
        if self.is_account_locked(user):
            return None
            
        return user
    
    async def create_access_token(self, user: User) -> str:
        """Create JWT access token with 30min expiry."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": expire
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token with 7 day expiry."""
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": expire
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload, None if invalid/expired."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt with cost factor 12."""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def increment_failed_attempts(self, email: str, db: AsyncSession) -> None:
        """Increment failed login attempts for user."""
        stmt = select(User).where(User.email == email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            await db.commit()
    
    async def reset_failed_attempts(self, user: User, db: AsyncSession) -> None:
        """Reset failed login attempts to 0."""
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
    
    def is_account_locked(self, user: User) -> bool:
        """Check if account is currently locked due to failed attempts."""
        if user.locked_until is None:
            return False
        return datetime.now(timezone.utc) < user.locked_until