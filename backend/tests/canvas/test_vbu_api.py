import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU

class TestVBUAPIAuth:
    async def test_list_vbus_admin(self, client: AsyncClient, admin_token: str):
        response = await client.get("/api/vbus", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert "data" in response.json()

    async def test_list_vbus_gm_filtered(self, client: AsyncClient, gm_token: str, gm_user: User):
        response = await client.get("/api/vbus", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        for vbu in data:
            assert vbu["gm_id"] == str(gm_user.id)

    async def test_list_vbus_viewer(self, client: AsyncClient, viewer_token: str):
        response = await client.get("/api/vbus", headers={"Authorization": f"Bearer {viewer_token}"})
        assert response.status_code == 200

    async def test_create_vbu_admin_success(self, client: AsyncClient, admin_token: str, gm_user: User):
        payload = {"name": "New VBU", "gm_id": str(gm_user.id)}
        response = await client.post("/api/vbus", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "New VBU"

    async def test_create_vbu_gm_forbidden(self, client: AsyncClient, gm_token: str, gm_user: User):
        payload = {"name": "New VBU", "gm_id": str(gm_user.id)}
        response = await client.post("/api/vbus", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403

    async def test_update_vbu_gm_own(self, client: AsyncClient, gm_token: str, gm_vbu: VBU):
        payload = {"name": "Updated Name"}
        response = await client.patch(f"/api/vbus/{gm_vbu.id}", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Name"

    async def test_update_vbu_gm_other_forbidden(self, client: AsyncClient, gm_token: str, other_vbu: VBU):
        payload = {"name": "Hacked"}
        response = await client.patch(f"/api/vbus/{other_vbu.id}", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403

    async def test_delete_vbu_admin_success(self, client: AsyncClient, admin_token: str, test_vbu: VBU):
        response = await client.delete(f"/api/vbus/{test_vbu.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 204

    async def test_delete_vbu_gm_forbidden(self, client: AsyncClient, gm_token: str, gm_vbu: VBU):
        response = await client.delete(f"/api/vbus/{gm_vbu.id}", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403

class TestVBUAPIValidation:
    async def test_create_vbu_invalid_name(self, client: AsyncClient, admin_token: str, gm_user: User):
        payload = {"name": "", "gm_id": str(gm_user.id)}
        response = await client.post("/api/vbus", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422

    async def test_create_vbu_invalid_gm_id(self, client: AsyncClient, admin_token: str):
        payload = {"name": "Valid Name", "gm_id": str(uuid4())}
        response = await client.post("/api/vbus", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422  # Service validates gm_id and returns 422 for invalid user

    async def test_get_vbu_not_found(self, client: AsyncClient, admin_token: str):
        response = await client.get(f"/api/vbus/{uuid4()}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 404

class TestVBUAPIPagination:
    async def test_list_vbus_pagination(self, client: AsyncClient, admin_token: str):
        response = await client.get("/api/vbus?page=1&per_page=10", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        meta = response.json()["meta"]
        assert "total" in meta
        assert "page" in meta
        assert "per_page" in meta