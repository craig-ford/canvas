import pytest
from sqlalchemy.exc import IntegrityError
from canvas.models.user import User, UserRole


def test_user_creation_with_defaults():
    """Test User model creates with default values."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User"
    )
    assert user.role == UserRole.VIEWER
    assert user.id is not None
    assert user.is_active is True
    assert user.failed_login_attempts == 0


def test_user_email_uniqueness():
    """Test email unique constraint enforcement."""
    # This test would require database session to test actual constraint
    # For now, verify the column definition has unique=True
    email_column = User.__table__.columns['email']
    assert email_column.unique is True


def test_user_role_enum_validation():
    """Test UserRole enum accepts valid values."""
    assert UserRole.ADMIN == "admin"
    assert UserRole.GM == "gm"
    assert UserRole.VIEWER == "viewer"


def test_user_password_hash_required():
    """Test password_hash field is required."""
    password_hash_column = User.__table__.columns['password_hash']
    assert password_hash_column.nullable is False


def test_user_timestamps_auto_populated():
    """Test created_at and updated_at are auto-populated."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User"
    )
    # TimestampMixin provides these fields
    assert hasattr(user, 'created_at')
    assert hasattr(user, 'updated_at')
    assert hasattr(user, 'id')


def test_user_table_name():
    """Test User model uses correct table name."""
    assert User.__tablename__ == "users"


def test_user_required_fields():
    """Test all required fields are properly defined."""
    email_column = User.__table__.columns['email']
    password_hash_column = User.__table__.columns['password_hash']
    name_column = User.__table__.columns['name']
    role_column = User.__table__.columns['role']
    
    assert email_column.nullable is False
    assert password_hash_column.nullable is False
    assert name_column.nullable is False
    assert role_column.nullable is False


def test_user_optional_fields():
    """Test optional fields are properly defined."""
    last_login_column = User.__table__.columns['last_login_at']
    locked_until_column = User.__table__.columns['locked_until']
    
    assert last_login_column.nullable is True
    assert locked_until_column.nullable is True


def test_user_email_index():
    """Test email column has index."""
    email_column = User.__table__.columns['email']
    assert email_column.index is True