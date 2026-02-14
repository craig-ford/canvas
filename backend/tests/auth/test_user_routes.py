import pytest
from httpx import AsyncClient
from fastapi import status
from canvas.models.user import User, UserRole
from canvas.auth.service import AuthService
from canvas.auth.user_service import UserService
from canvas.auth.dependencies import get_current_user, require_role
from canvas import success_response, list_response


class TestUserManagementRoutes:
    """Test admin user management endpoints with authorization."""
    
    @pytest.mark.asyncio
    async def test_get_users_admin_success(self, client: AsyncClient, admin_token: str):
        """Test admin can list all users."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "meta" in data
        assert "total" in data["meta"]
    
    @pytest.mark.asyncio
    async def test_get_users_non_admin_forbidden(self, client: AsyncClient, gm_token: str):
        """Test non-admin cannot list users."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.get("/api/users", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    @pytest.mark.asyncio
    async def test_get_users_no_auth_unauthorized(self, client: AsyncClient):
        """Test unauthenticated request returns 401."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.get("/api/users")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    @pytest.mark.asyncio
    async def test_update_user_role_admin_success(self, client: AsyncClient, admin_token: str, sample_user: User):
        """Test admin can update user role."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.patch(
            f"/api/users/{sample_user.id}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert data["data"]["role"] == "admin"
        assert data["data"]["id"] == str(sample_user.id)
    
    @pytest.mark.asyncio
    async def test_update_user_role_non_admin_forbidden(self, client: AsyncClient, gm_token: str, sample_user: User):
        """Test non-admin cannot update user role."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.patch(
            f"/api/users/{sample_user.id}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    @pytest.mark.asyncio
    async def test_update_user_role_invalid_role(self, client: AsyncClient, admin_token: str, sample_user: User):
        """Test invalid role returns validation error."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.patch(
            f"/api/users/{sample_user.id}",
            json={"role": "invalid"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    @pytest.mark.asyncio
    async def test_update_user_role_nonexistent_user(self, client: AsyncClient, admin_token: str):
        """Test updating nonexistent user returns 404."""
        from uuid import uuid4
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.patch(
            f"/api/users/{uuid4()}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_delete_user_admin_success(self, client: AsyncClient, admin_token: str, sample_user: User):
        """Test admin can delete user."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.delete(
            f"/api/users/{sample_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_delete_user_non_admin_forbidden(self, client: AsyncClient, gm_token: str, sample_user: User):
        """Test non-admin cannot delete user."""
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.delete(
            f"/api/users/{sample_user.id}",
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    @pytest.mark.asyncio
    async def test_delete_user_nonexistent_user(self, client: AsyncClient, admin_token: str):
        """Test deleting nonexistent user returns 404."""
        from uuid import uuid4
        # BLOCKED: awaiting T-016 auth routes implementation
        response = await client.delete(
            f"/api/users/{uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"


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
async def admin_token(db):
    """Create admin user and return JWT token."""
    auth_service = AuthService()
    admin_user = await auth_service.register_user("admin@test.local", "password123", "Admin User", "admin", db)
    return await auth_service.create_access_token(admin_user)


@pytest.fixture
async def gm_token(db):
    """Create GM user and return JWT token."""
    auth_service = AuthService()
    gm_user = await auth_service.register_user("gm@test.local", "password123", "GM User", "gm", db)
    return await auth_service.create_access_token(gm_user)


@pytest.fixture
async def sample_user(db):
    """Create sample user for testing."""
    auth_service = AuthService()
    return await auth_service.register_user("sample@test.local", "password123", "Sample User", "viewer", db)


@pytest.fixture
async def db():
    """Create test database session."""
    from canvas.db import get_db_session
    async for session in get_db_session():
        yield session
        break