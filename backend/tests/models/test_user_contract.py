import pytest
from sqlalchemy import Column, String, Enum as SQLEnum, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from canvas.models.user import User, UserRole
from canvas.models import TimestampMixin


def test_user_role_enum_values():
    """Test UserRole enum has correct values."""
    assert UserRole.ADMIN == "admin"
    assert UserRole.GM == "gm"
    assert UserRole.VIEWER == "viewer"


def test_user_inherits_timestamp_mixin():
    """Test User model inherits from TimestampMixin."""
    assert issubclass(User, TimestampMixin)


def test_user_table_name():
    """Test User model has correct table name."""
    assert User.__tablename__ == "users"


def test_user_has_required_columns():
    """Test User model has all required columns with correct types."""
    # Check column exists and type
    assert hasattr(User, 'email')
    assert isinstance(User.email.type, String)
    assert User.email.type.length == 255
    assert User.email.unique is True
    assert User.email.nullable is False
    assert User.email.index is True
    
    assert hasattr(User, 'password_hash')
    assert isinstance(User.password_hash.type, String)
    assert User.password_hash.type.length == 255
    assert User.password_hash.nullable is False
    
    assert hasattr(User, 'name')
    assert isinstance(User.name.type, String)
    assert User.name.type.length == 255
    assert User.name.nullable is False
    
    assert hasattr(User, 'role')
    assert isinstance(User.role.type, SQLEnum)
    assert User.role.nullable is False
    assert User.role.default.arg == UserRole.VIEWER
    
    assert hasattr(User, 'is_active')
    assert isinstance(User.is_active.type, Boolean)
    assert User.is_active.nullable is False
    assert User.is_active.default.arg is True
    
    assert hasattr(User, 'last_login_at')
    assert isinstance(User.last_login_at.type, DateTime)
    assert User.last_login_at.nullable is True
    
    assert hasattr(User, 'failed_login_attempts')
    assert isinstance(User.failed_login_attempts.type, Integer)
    assert User.failed_login_attempts.nullable is False
    assert User.failed_login_attempts.default.arg == 0
    
    assert hasattr(User, 'locked_until')
    assert isinstance(User.locked_until.type, DateTime)
    assert User.locked_until.nullable is True


def test_user_inherits_timestamp_columns():
    """Test User model inherits timestamp columns from TimestampMixin."""
    assert hasattr(User, 'id')
    assert isinstance(User.id.type, UUID)
    assert User.id.primary_key is True
    
    assert hasattr(User, 'created_at')
    assert isinstance(User.created_at.type, DateTime)
    assert User.created_at.nullable is False
    
    assert hasattr(User, 'updated_at')
    assert isinstance(User.updated_at.type, DateTime)
    assert User.updated_at.nullable is False


def test_user_model_can_be_imported():
    """Test User model can be imported without error."""
    from canvas.models.user import User, UserRole
    assert User is not None
    assert UserRole is not None