import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.auth.service import AuthService


class TestAuthRoutesIntegration:
    """Integration tests for auth routes with real database and JWT."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, authed_client: AsyncClient, db: AsyncSession):
        """POST /api/auth/register with admin auth creates user."""
        response = await authed_client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "Password1!",
            "name": "New User",
            "role": "viewer"
        })
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["name"] == "New User"
        assert data["data"]["role"] == "viewer"
        assert "password_hash" not in data["data"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, authed_client: AsyncClient, db: AsyncSession):
        """POST /api/auth/register with existing email returns 409."""
        auth_service = AuthService()
        await auth_service.register_user("existing@example.com", "Password1!", "Existing", "viewer", db)

        response = await authed_client.post("/api/auth/register", json={
            "email": "existing@example.com",
            "password": "Password1!",
            "name": "Duplicate",
            "role": "viewer"
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_requires_admin(self, client: AsyncClient, gm_token, db: AsyncSession):
        """POST /api/auth/register without admin role returns 403."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "x@example.com", "password": "Password1!", "name": "X", "role": "viewer"},
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db: AsyncSession):
        """POST /api/auth/login with valid credentials returns tokens."""
        auth_service = AuthService()
        await auth_service.register_user("login@example.com", "Password1!", "Login User", "gm", db)

        response = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Password1!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "login@example.com"
        assert data["data"]["user"]["role"] == "gm"
        # refresh_token is set as httpOnly cookie, not in response body
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, db: AsyncSession):
        """POST /api/auth/login with wrong password returns 401."""
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_account_locked(self, client: AsyncClient, db: AsyncSession):
        """POST /api/auth/login with locked account returns 401."""
        auth_service = AuthService()
        await auth_service.register_user("locked@example.com", "Password1!", "Locked", "viewer", db)

        for _ in range(5):
            await auth_service.increment_failed_attempts("locked@example.com", db)

        response = await client.post("/api/auth/login", json={
            "email": "locked@example.com",
            "password": "Password1!"
        })
        # Locked account: authenticate_user returns None → 401
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, db: AsyncSession):
        """POST /api/auth/refresh with valid cookie returns new access token."""
        auth_service = AuthService()
        user = await auth_service.register_user("refresh@example.com", "Password1!", "Refresh", "viewer", db)
        refresh_token = await auth_service.create_refresh_token(user)

        response = await client.post("/api/auth/refresh", cookies={"refresh_token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient, db: AsyncSession):
        """POST /api/auth/refresh with invalid token returns 401."""
        response = await client.post("/api/auth/refresh", cookies={"refresh_token": "invalid_token"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient, db: AsyncSession):
        """GET /api/auth/me with valid token returns user profile."""
        auth_service = AuthService()
        user = await auth_service.register_user("profile@example.com", "Password1!", "Profile", "admin", db)
        access_token = await auth_service.create_access_token(user)

        response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["email"] == "profile@example.com"
        assert data["data"]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient, db: AsyncSession):
        """GET /api/auth/me with invalid token returns 401/403."""
        response = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
        # HTTPBearer returns 403 for invalid credentials
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_rate_limiting_login(self, client: AsyncClient, db: AsyncSession):
        """Multiple failed login attempts trigger rate limiting."""
        from canvas.auth.routes import rate_limit_store
        rate_limit_store.clear()
        auth_service = AuthService()
        await auth_service.register_user("ratelimit@example.com", "Password1!", "Rate", "viewer", db)

        # Make 5 requests to trigger rate limiting
        for _ in range(5):
            response = await client.post("/api/auth/login", json={
                "email": "ratelimit@example.com",
                "password": "wrongpassword"
            })
            assert response.status_code == 401

        # 6th request should be rate limited
        response = await client.post("/api/auth/login", json={
            "email": "ratelimit@example.com",
            "password": "Password1!"
        })
        assert response.status_code == 429
