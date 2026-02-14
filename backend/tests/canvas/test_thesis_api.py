import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis

class TestThesisAPIAuth:
    async def test_get_theses_admin(self, client: AsyncClient, admin_token: str, test_canvas: Canvas):
        response = await client.get(f"/api/canvases/{test_canvas.id}/theses", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert "data" in response.json()

    async def test_get_theses_gm_own(self, client: AsyncClient, gm_token: str, gm_canvas: Canvas):
        response = await client.get(f"/api/canvases/{gm_canvas.id}/theses", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200

    async def test_get_theses_gm_other_forbidden(self, client: AsyncClient, gm_token: str, other_canvas: Canvas):
        response = await client.get(f"/api/canvases/{other_canvas.id}/theses", headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403

    async def test_create_thesis_gm_own(self, client: AsyncClient, gm_token: str, gm_canvas: Canvas):
        payload = {"text": "New thesis", "order": 1}
        response = await client.post(f"/api/canvases/{gm_canvas.id}/theses", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 201
        assert response.json()["data"]["text"] == "New thesis"

    async def test_create_thesis_viewer_forbidden(self, client: AsyncClient, viewer_token: str, test_canvas: Canvas):
        payload = {"text": "Forbidden thesis", "order": 1}
        response = await client.post(f"/api/canvases/{test_canvas.id}/theses", json=payload, headers={"Authorization": f"Bearer {viewer_token}"})
        assert response.status_code == 403

    async def test_update_thesis_gm_own(self, client: AsyncClient, gm_token: str, gm_thesis: Thesis):
        payload = {"text": "Updated thesis"}
        response = await client.patch(f"/api/theses/{gm_thesis.id}", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 200
        assert response.json()["data"]["text"] == "Updated thesis"

    async def test_delete_thesis_admin(self, client: AsyncClient, admin_token: str, test_thesis: Thesis):
        response = await client.delete(f"/api/theses/{test_thesis.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 204

class TestThesisAPIValidation:
    async def test_create_thesis_empty_text(self, client: AsyncClient, admin_token: str, test_canvas: Canvas):
        payload = {"text": "", "order": 1}
        response = await client.post(f"/api/canvases/{test_canvas.id}/theses", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422

    async def test_create_thesis_invalid_order(self, client: AsyncClient, admin_token: str, test_canvas: Canvas):
        payload = {"text": "Valid text", "order": 6}
        response = await client.post(f"/api/canvases/{test_canvas.id}/theses", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422

    async def test_create_thesis_duplicate_order(self, client: AsyncClient, admin_token: str, canvas_with_thesis: Canvas):
        payload = {"text": "Duplicate order", "order": 1}
        response = await client.post(f"/api/canvases/{canvas_with_thesis.id}/theses", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 409

    async def test_thesis_not_found(self, client: AsyncClient, admin_token: str):
        response = await client.get(f"/api/theses/{uuid4()}", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 404

class TestThesisAPIReordering:
    async def test_reorder_theses_success(self, client: AsyncClient, admin_token: str, canvas_with_multiple_theses: Canvas):
        theses = canvas_with_multiple_theses.theses
        payload = {
            "thesis_orders": [
                {"id": str(theses[1].id), "order": 1},
                {"id": str(theses[0].id), "order": 2}
            ]
        }
        response = await client.put(f"/api/canvases/{canvas_with_multiple_theses.id}/theses/reorder", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

    async def test_reorder_theses_invalid_order(self, client: AsyncClient, admin_token: str, canvas_with_thesis: Canvas):
        thesis = canvas_with_thesis.theses[0]
        payload = {
            "thesis_orders": [
                {"id": str(thesis.id), "order": 6}
            ]
        }
        response = await client.put(f"/api/canvases/{canvas_with_thesis.id}/theses/reorder", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 422

    async def test_reorder_theses_gm_other_forbidden(self, client: AsyncClient, gm_token: str, other_canvas_with_theses: Canvas):
        thesis = other_canvas_with_theses.theses[0]
        payload = {
            "thesis_orders": [
                {"id": str(thesis.id), "order": 1}
            ]
        }
        response = await client.put(f"/api/canvases/{other_canvas_with_theses.id}/theses/reorder", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert response.status_code == 403