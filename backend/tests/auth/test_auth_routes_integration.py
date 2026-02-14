import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User, UserRole
from canvas.auth.service import AuthService
from canvas.auth.dependencies import get_current_user, require_role
from canvas import success_response


class TestAuthRoutesIntegration:
    """Integration tests for auth routes with real database and JWT."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful user registration."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/register", json={
            "email": "newuser@canvas.local",
            "password": "password123",
            "name": "New User",
            "role": "viewer"
        })
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "newuser@canvas.local"
        assert data["data"]["name"] == "New User"
        assert data["data"]["role"] == "viewer"
        assert "password_hash" not in data["data"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, db: AsyncSession):
        """Test registration with duplicate email returns 409."""
        # Create user first
        auth_service = AuthService()
        await auth_service.register_user("existing@canvas.local", "password123", "Existing User", "viewer", db)
        
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/register", json={
            "email": "existing@canvas.local",
            "password": "password123",
            "name": "Duplicate User",
            "role": "viewer"
        })
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "CONFLICT"
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful login returns tokens and user data."""
        # Create test user
        auth_service = AuthService()
        user = await auth_service.register_user("login@canvas.local", "password123", "Login User", "gm", db)
        
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/login", json={
            "email": "login@canvas.local",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "login@canvas.local"
        assert data["data"]["user"]["role"] == "gm"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, db: AsyncSession):
        """Test login with invalid credentials returns 401."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@canvas.local",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert "Invalid email or password" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_login_account_locked(self, client: AsyncClient, db: AsyncSession):
        """Test login with locked account returns 429."""
        # Create user and lock account
        auth_service = AuthService()
        user = await auth_service.register_user("locked@canvas.local", "password123", "Locked User", "viewer", db)
        
        # Simulate failed attempts to lock account
        for _ in range(5):
            await auth_service.increment_failed_attempts("locked@canvas.local", db)
        
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/login", json={
            "email": "locked@canvas.local",
            "password": "password123"
        })
        assert response.status_code == 429
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "TOO_MANY_REQUESTS"
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful token refresh."""
        # Create user and get tokens
        auth_service = AuthService()
        user = await auth_service.register_user("refresh@canvas.local", "password123", "Refresh User", "viewer", db)
        refresh_token = await auth_service.create_refresh_token(user)
        
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/refresh", cookies={"refresh_token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient, db: AsyncSession):
        """Test refresh with invalid token returns 401."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.post("/api/auth/refresh", cookies={"refresh_token": "invalid_token"})
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient, db: AsyncSession):
        """Test GET /api/auth/me with valid token."""
        # Create user and get access token
        auth_service = AuthService()
        user = await auth_service.register_user("profile@canvas.local", "password123", "Profile User", "admin", db)
        access_token = await auth_service.create_access_token(user)
        
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "profile@canvas.local"
        assert data["data"]["name"] == "Profile User"
        assert data["data"]["role"] == "admin"
        assert "password_hash" not in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient, db: AsyncSession):
        """Test GET /api/auth/me with invalid token returns 401."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    @pytest.mark.asyncio
    async def test_rate_limiting_login(self, client: AsyncClient, db: AsyncSession):
        """Test login rate limiting after 5 failed attempts."""
        # BLOCKED: awaiting T-016 auth routes implementation
        # Make 6 failed login attempts
        for i in range(6):
            response = await client.post("/api/auth/login", json={
                "email": "ratelimit@canvas.local",
                "password": "wrongpassword"
            })
            if i < 5:
                assert response.status_code == 401
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429
                data = response.json()
                assert "error" in data
                assert data["error"]["code"] == "TOO_MANY_REQUESTS"


@pytest.fixture
async def client():
    """Create test HTTP client."""
    # BLOCKED: awaiting T-016 auth routes implementation
    from httpx import AsyncClient
    from canvas.main import create_app
    
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db():
    """Create test database session."""
    from canvas.db import get_db_session
    async for session in get_db_session():
        yield session
        break