import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane

class TestCanvasAPIAuth:
    async def test_get_canvas_admin(self, client: AsyncClient, admin_token: str, test_vbu: VBU):
        response = await client.get(f"/api/vbus/{test_vbu.id}/canvas", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert response.json()["data"]["vbu_id"] == str(test_vbu.id)

    async def test_get_canvas_gm_own(self, client: AsyncClient, gm_token: str, gm_vbu: VBU):
        response = await client.get(f"/api/vbus/{gm_vbu.id}/canvas", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200

    async def test_get_canvas_gm_other_forbidden(self, client: AsyncClient, gm_token: str, other_vbu: VBU):
        response = await client.get(f"/api/vbus/{other_vbu.id}/canvas", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403

    async def test_get_canvas_viewer(self, client: AsyncClient, viewer_token: str, test_vbu: VBU):
        response = await client.get(f"/api/vbus/{test_vbu.id}/canvas", headers={"Authorization": f"Bearer {viewer_token}"})
        assert response.status_code == 200

    async def test_update_canvas_gm_own(self, client: AsyncClient, gm_token: str, gm_vbu: VBU):
        payload = {"lifecycle_lane": "sell", "product_name": "Updated Product"}
        response = await client.put(f"/api/vbus/{gm_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["lifecycle_lane"] == "sell"
        assert data["product_name"] == "Updated Product"

    async def test_update_canvas_viewer_forbidden(self, client: AsyncClient, viewer_token: str, test_vbu: VBU):
        payload = {"lifecycle_lane": "milk"}
        response = await client.put(f"/api/vbus/{test_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {viewer_token}"})
        assert response.status_code == 403

class TestCanvasAPINestedData:
    async def test_get_canvas_with_theses(self, client: AsyncClient, admin_token: str, canvas_with_theses: Canvas):
        response = await client.get(f"/api/vbus/{canvas_with_theses.vbu_id}/canvas", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert "theses" in data
        assert len(data["theses"]) > 0

    async def test_get_canvas_with_proof_points(self, client: AsyncClient, admin_token: str, canvas_with_proof_points: Canvas):
        response = await client.get(f"/api/vbus/{canvas_with_proof_points.vbu_id}/canvas", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        thesis = data["theses"][0]
        assert "proof_points" in thesis
        assert len(thesis["proof_points"]) > 0

class TestCanvasAPIValidation:
    async def test_update_canvas_invalid_lifecycle_lane(self, client: AsyncClient, admin_token: str, test_vbu: VBU):
        payload = {"lifecycle_lane": "invalid"}
        response = await client.put(f"/api/vbus/{test_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422

    async def test_update_canvas_empty_product_name(self, client: AsyncClient, admin_token: str, test_vbu: VBU):
        payload = {"product_name": ""}
        response = await client.put(f"/api/vbus/{test_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422  # Pydantic validation rejects empty product_name

    async def test_get_canvas_vbu_not_found(self, client: AsyncClient, admin_token: str):
        response = await client.get(f"/api/vbus/{uuid4()}/canvas", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 404

class TestCanvasAPIPortfolioNotes:
    async def test_update_portfolio_notes_admin(self, client: AsyncClient, admin_token: str, test_vbu: VBU):
        payload = {"portfolio_notes": "Admin notes"}
        response = await client.put(f"/api/vbus/{test_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert response.json()["data"]["portfolio_notes"] == "Admin notes"

    async def test_update_portfolio_notes_gm_ignored(self, client: AsyncClient, gm_token: str, gm_vbu: VBU):
        payload = {"portfolio_notes": "GM notes", "product_name": "Valid Update"}
        response = await client.put(f"/api/vbus/{gm_vbu.id}/canvas", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["product_name"] == "Valid Update"
        assert data["portfolio_notes"] is None  # Filtered out for GM users