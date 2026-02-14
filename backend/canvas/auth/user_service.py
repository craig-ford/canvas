from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User, UserRole

class UserService:
    """User management service for admin operations."""
    
    async def list_users(self, db: AsyncSession) -> List[User]:
        """List all users in the system."""
        result = await db.execute(select(User))
        return result.scalars().all()
    
    async def update_user_role(self, user_id: UUID, role: UserRole, db: AsyncSession) -> User:
        """Update a user's role. Raises ValueError if user not found."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.role = role
        await db.commit()
        await db.refresh(user)
        return user
    
    async def delete_user(self, user_id: UUID, db: AsyncSession) -> None:
        """Delete a user. Raises ValueError if user not found."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        await db.delete(user)
        await db.commit()
    
    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        """Find user by email address (case-insensitive)."""
        result = await db.execute(
            select(User).where(func.lower(User.email) == func.lower(email))
        )
        return result.scalar_one_or_none()