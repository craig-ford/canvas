from enum import Enum
from sqlalchemy import Column, String, Enum as SQLEnum, Boolean, Integer, DateTime
from canvas.models import Base, TimestampMixin

class UserRole(str, Enum):
    ADMIN = "admin"
    GM = "gm" 
    VIEWER = "viewer"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)