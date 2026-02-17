import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.auth.service import AuthService


class TestUserManagementRoutes:
    """Integration tests for user management routes (admin only)."""

    @pytest.mark.asyncio
    async def test_get_users_admin_success(self, authed_client: AsyncClient, db: AsyncSession):
        """GET /api/auth/users as admin returns user list."""
        response = await authed_client.get("/api/auth/users")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "meta" in data
        assert "total" in data["meta"]

    @pytest.mark.asyncio
    async def test_get_users_non_admin_forbidden(self, client: AsyncClient, gm_token, db: AsyncSession):
        """GET /api/auth/users as GM returns 403."""
        response = await client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_users_no_auth_unauthorized(self, client: AsyncClient):
        """GET /api/auth/users without auth returns 401."""
        response = await client.get("/api/auth/users")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_role_admin_success(self, authed_client: AsyncClient, gm_user, db: AsyncSession):
        """PATCH /api/auth/users/{id} as admin updates role."""
        response = await authed_client.patch(
            f"/api/auth/users/{gm_user.id}",
            json={"role": "viewer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["role"] == "viewer"

    @pytest.mark.asyncio
    async def test_update_user_role_non_admin_forbidden(self, client: AsyncClient, gm_token, gm_user, db: AsyncSession):
        """PATCH /api/auth/users/{id} as GM returns 403."""
        response = await client.patch(
            f"/api/auth/users/{gm_user.id}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_user_role_invalid_role(self, authed_client: AsyncClient, gm_user, db: AsyncSession):
        """PATCH /api/auth/users/{id} with invalid role returns 422."""
        response = await authed_client.patch(
            f"/api/auth/users/{gm_user.id}",
            json={"role": "superadmin"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_user_role_nonexistent_user(self, authed_client: AsyncClient, db: AsyncSession):
        """PATCH /api/auth/users/{id} with nonexistent user returns 404."""
        from uuid import uuid4
        response = await authed_client.patch(
            f"/api/auth/users/{uuid4()}",
            json={"role": "viewer"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_admin_success(self, authed_client: AsyncClient, viewer_user, db: AsyncSession):
        """DELETE /api/auth/users/{id} as admin deletes user."""
        response = await authed_client.delete(f"/api/auth/users/{viewer_user.id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_user_non_admin_forbidden(self, client: AsyncClient, gm_token, viewer_user, db: AsyncSession):
        """DELETE /api/auth/users/{id} as GM returns 403."""
        response = await client.delete(
            f"/api/auth/users/{viewer_user.id}",
            headers={"Authorization": f"Bearer {gm_token}"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_user_nonexistent_user(self, authed_client: AsyncClient, db: AsyncSession):
        """DELETE /api/auth/users/{id} with nonexistent user returns 404."""
        from uuid import uuid4
        response = await authed_client.delete(f"/api/auth/users/{uuid4()}")
        assert response.status_code == 404
