import uuid
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
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER, server_default='viewer')
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0, server_default='0')
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    def __init__(self, **kwargs):
        # Set Python-level defaults
        if 'role' not in kwargs:
            kwargs['role'] = UserRole.VIEWER
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'failed_login_attempts' not in kwargs:
            kwargs['failed_login_attempts'] = 0
        super().__init__(**kwargs)
        # Ensure id is generated if not provided
        if self.id is None:
            self.id = uuid.uuid4()