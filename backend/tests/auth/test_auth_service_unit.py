import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
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
def mock_db_session():
    """Create mock database session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def test_user():
    """Create test user for testing."""
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


class TestAuthServiceUnit:
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_db_session):
        """Test successful user registration with password hashing."""
        email = "new@example.com"
        password = "password123"
        name = "New User"
        role = "viewer"
        
        # Mock the database operations
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await auth_service.register_user(email, password, name, role, mock_db_session)
        
        # Verify user was created with correct data
        assert result.email == email.lower()
        assert result.name == name
        assert result.role == UserRole.VIEWER
        assert auth_service.pwd_context.verify(password, result.password_hash)
        
        # Verify database operations were called
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_valid_credentials(self, auth_service, mock_db_session, test_user):
        """Test authentication with valid email and password."""
        email = "test@example.com"
        password = "password123"
        
        # Hash the password for the test user
        test_user.password_hash = auth_service.pwd_context.hash(password)
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service.authenticate_user(email, password, mock_db_session)
        
        assert result == test_user
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, mock_db_session, test_user):
        """Test authentication fails with invalid password."""
        email = "test@example.com"
        password = "wrong_password"
        
        # Hash a different password for the test user
        test_user.password_hash = auth_service.pwd_context.hash("correct_password")
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service.authenticate_user(email, password, mock_db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent_email(self, auth_service, mock_db_session):
        """Test authentication fails with nonexistent email."""
        email = "nonexistent@example.com"
        password = "password123"
        
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service.authenticate_user(email, password, mock_db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_locked_account(self, auth_service, mock_db_session, test_user):
        """Test authentication fails with locked account."""
        email = "test@example.com"
        password = "password123"
        
        # Set up locked account
        test_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
        test_user.password_hash = auth_service.pwd_context.hash(password)
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service.authenticate_user(email, password, mock_db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service, test_user):
        """Test access token creation with 30min expiry."""
        token = await auth_service.create_access_token(test_user)
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
        
        # Verify token payload
        payload = await auth_service.verify_token(token)
        assert payload["sub"] == str(test_user.id)
        assert payload["email"] == test_user.email
        assert payload["role"] == test_user.role.value
        
        # Verify expiry is approximately 30 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=30)
        assert abs((exp_time - expected_exp).total_seconds()) < 60  # Within 1 minute
    
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, auth_service, test_user):
        """Test refresh token creation with 7 day expiry."""
        token = await auth_service.create_refresh_token(test_user)
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
        
        # Verify token payload
        payload = await auth_service.verify_token(token)
        assert payload["sub"] == str(test_user.id)
        assert payload["type"] == "refresh"
        
        # Verify expiry is approximately 7 days from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(days=7)
        assert abs((exp_time - expected_exp).total_seconds()) < 3600  # Within 1 hour
    
    @pytest.mark.asyncio
    async def test_verify_token_valid(self, auth_service, test_user):
        """Test token verification with valid JWT."""
        token = await auth_service.create_access_token(test_user)
        payload = await auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(test_user.id)
        assert payload["email"] == test_user.email
        assert payload["role"] == test_user.role.value
    
    @pytest.mark.asyncio
    async def test_verify_token_expired(self, auth_service, test_user):
        """Test token verification fails with expired JWT."""
        # Create token with past expiry
        with patch('canvas.auth.service.datetime') as mock_datetime:
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            mock_datetime.now.return_value = past_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            token = await auth_service.create_access_token(test_user)
        
        # Verify token is now expired
        payload = await auth_service.verify_token(token)
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid_signature(self, auth_service):
        """Test token verification fails with invalid signature."""
        # Create token with different secret
        different_service = AuthService(MagicMock(
            secret_key="different-secret",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7
        ))
        
        test_user = MagicMock()
        test_user.id = uuid4()
        test_user.email = "test@example.com"
        test_user.role = UserRole.VIEWER
        
        token = await different_service.create_access_token(test_user)
        
        # Verify token fails with original service
        payload = await auth_service.verify_token(token)
        assert payload is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_service, mock_db_session, test_user):
        """Test getting user by ID."""
        user_id = test_user.id
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service.get_user_by_id(user_id, mock_db_session)
        
        assert result == test_user
        mock_db_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_increment_failed_attempts(self, auth_service, mock_db_session, test_user):
        """Test failed login attempt counter increments."""
        email = "test@example.com"
        test_user.failed_login_attempts = 2
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        
        await auth_service.increment_failed_attempts(email, mock_db_session)
        
        assert test_user.failed_login_attempts == 3
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_increment_failed_attempts_locks_after_five(self, auth_service, mock_db_session, test_user):
        """Test account locks after 5 failed attempts."""
        email = "test@example.com"
        test_user.failed_login_attempts = 4
        test_user.locked_until = None
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        
        await auth_service.increment_failed_attempts(email, mock_db_session)
        
        assert test_user.failed_login_attempts == 5
        assert test_user.locked_until is not None
        assert test_user.locked_until > datetime.now(timezone.utc)
    
    @pytest.mark.asyncio
    async def test_reset_failed_attempts(self, auth_service, mock_db_session, test_user):
        """Test failed attempts reset on successful login."""
        test_user.failed_login_attempts = 3
        test_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=5)
        test_user.last_login_at = None
        
        mock_db_session.commit = AsyncMock()
        
        await auth_service.reset_failed_attempts(test_user, mock_db_session)
        
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None
        assert test_user.last_login_at is not None
        mock_db_session.commit.assert_called_once()
    
    def test_is_account_locked_no_lockout(self, auth_service, test_user):
        """Test account not locked when no lockout set."""
        test_user.locked_until = None
        
        result = auth_service.is_account_locked(test_user)
        
        assert result is False
    
    def test_is_account_locked_expired_lockout(self, auth_service, test_user):
        """Test account not locked when lockout has expired."""
        test_user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        result = auth_service.is_account_locked(test_user)
        
        assert result is False
    
    def test_is_account_locked_active_lockout(self, auth_service, test_user):
        """Test account locked when lockout is active."""
        test_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        result = auth_service.is_account_locked(test_user)
        
        assert result is True
    
    def test_password_hashing_bcrypt_cost_12(self, auth_service):
        """Test password hashing uses bcrypt with cost factor 12."""
        password = "test_password_123"
        hashed = auth_service.pwd_context.hash(password)
        
        # Verify bcrypt format with cost 12
        assert hashed.startswith("$2b$12$")
        assert len(hashed) >= 60  # bcrypt hashes are at least 60 chars
        
        # Verify password verification works
        assert auth_service.pwd_context.verify(password, hashed)
        assert not auth_service.pwd_context.verify("wrong_password", hashed)