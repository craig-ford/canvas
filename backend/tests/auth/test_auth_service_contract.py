import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from canvas.auth.service import AuthService
from canvas.models.user import User, UserRole
from canvas.config import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = MagicMock(spec=Settings)
    settings.secret_key = "test-secret-key-for-testing"
    settings.access_token_expire_minutes = 30
    settings.refresh_token_expire_days = 7
    return settings


@pytest.fixture
def auth_service(mock_settings):
    """Create AuthService instance for testing."""
    return AuthService(settings=mock_settings)


@pytest.fixture
def mock_user():
    """Create mock user for testing."""
    user = MagicMock()
    user.id = uuid4()
    user.email = "test@example.com"
    user.password_hash = "$2b$12$test_hash"
    user.name = "Test User"
    user.role = UserRole.VIEWER
    user.is_active = True
    user.failed_login_attempts = 0
    user.locked_until = None
    return user


def test_auth_service_has_required_methods(auth_service):
    """Test AuthService has all required methods with correct signatures."""
    assert hasattr(auth_service, 'register_user')
    assert hasattr(auth_service, 'authenticate_user')
    assert hasattr(auth_service, 'create_access_token')
    assert hasattr(auth_service, 'create_refresh_token')
    assert hasattr(auth_service, 'verify_token')
    assert hasattr(auth_service, 'get_user_by_id')
    assert hasattr(auth_service, 'increment_failed_attempts')
    assert hasattr(auth_service, 'reset_failed_attempts')
    assert hasattr(auth_service, 'is_account_locked')


def test_auth_service_uses_bcrypt_cost_12(auth_service):
    """Test AuthService uses bcrypt with cost factor 12."""
    assert "bcrypt" in auth_service.pwd_context.schemes()
    # Test that a hashed password starts with bcrypt identifier for cost 12
    test_password = "test123"
    hashed = auth_service.pwd_context.hash(test_password)
    assert hashed.startswith("$2b$12$")


def test_auth_service_uses_hs256_algorithm(auth_service):
    """Test AuthService uses HS256 algorithm for JWT."""
    assert auth_service.algorithm == "HS256"


def test_password_hashing_and_verification(auth_service):
    """Test password hashing and verification works correctly."""
    password = "test_password_123"
    hashed = auth_service.pwd_context.hash(password)
    
    # Hash should be different from plaintext
    assert hashed != password
    # Hash should start with bcrypt identifier
    assert hashed.startswith("$2b$12$")
    # Verification should work
    assert auth_service.pwd_context.verify(password, hashed)
    # Wrong password should fail
    assert not auth_service.pwd_context.verify("wrong_password", hashed)


@pytest.mark.asyncio
async def test_create_access_token_structure(auth_service, mock_user):
    """Test access token creation returns valid JWT structure."""
    token = await auth_service.create_access_token(mock_user)
    
    # JWT should have 3 parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3
    
    # Verify token payload
    payload = await auth_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(mock_user.id)
    assert payload["email"] == mock_user.email
    assert payload["role"] == mock_user.role.value
    assert "exp" in payload


@pytest.mark.asyncio
async def test_create_refresh_token_structure(auth_service, mock_user):
    """Test refresh token creation returns valid JWT structure."""
    token = await auth_service.create_refresh_token(mock_user)
    
    # JWT should have 3 parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3
    
    # Verify token payload
    payload = await auth_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(mock_user.id)
    assert payload["type"] == "refresh"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_verify_token_with_invalid_token(auth_service):
    """Test verify_token returns None for invalid tokens."""
    # Invalid token format
    result = await auth_service.verify_token("invalid.token")
    assert result is None
    
    # Empty token
    result = await auth_service.verify_token("")
    assert result is None
    
    # Malformed JWT
    result = await auth_service.verify_token("not.a.jwt.token")
    assert result is None


def test_is_account_locked_with_no_lockout(auth_service, mock_user):
    """Test is_account_locked returns False when no lockout set."""
    mock_user.locked_until = None
    assert not auth_service.is_account_locked(mock_user)


def test_is_account_locked_with_expired_lockout(auth_service, mock_user):
    """Test is_account_locked returns False when lockout has expired."""
    mock_user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert not auth_service.is_account_locked(mock_user)


def test_is_account_locked_with_active_lockout(auth_service, mock_user):
    """Test is_account_locked returns True when lockout is active."""
    mock_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
    assert auth_service.is_account_locked(mock_user)


def test_auth_service_can_be_imported():
    """Test AuthService can be imported without error."""
    from canvas.auth.service import AuthService
    assert AuthService is not None