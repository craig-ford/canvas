import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from datetime import date

class TestReviewAPIIntegration:
    async def test_list_reviews_admin_access_all_canvases(self, client: AsyncClient, admin_token, canvas, canvas_b):
        """Test admin can list reviews for any canvas"""
        resp = await client.get(f"/api/canvases/{canvas.id}/reviews", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == status.HTTP_200_OK
        resp_b = await client.get(f"/api/canvases/{canvas_b.id}/reviews", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp_b.status_code == status.HTTP_200_OK

    async def test_list_reviews_gm_access_own_canvas_only(self, client: AsyncClient, gm_token, own_canvas, other_canvas):
        """Test GM can only list reviews for own VBU canvas"""
        resp = await client.get(f"/api/canvases/{own_canvas.id}/reviews", headers={"Authorization": f"Bearer {gm_token}"})
        assert resp.status_code == status.HTTP_200_OK
        resp_other = await client.get(f"/api/canvases/{other_canvas.id}/reviews", headers={"Authorization": f"Bearer {gm_token}"})
        assert resp_other.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_reviews_viewer_access_all_readonly(self, client: AsyncClient, viewer_token, canvas):
        """Test viewer can list reviews for any canvas (read-only)"""
        resp = await client.get(f"/api/canvases/{canvas.id}/reviews", headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp.status_code == status.HTTP_200_OK

    async def test_create_review_admin_any_canvas(self, client: AsyncClient, admin_token, canvas, test_thesis):
        """Test admin can create review for any canvas"""
        payload = {
            "review_date": str(date.today()), 
            "currently_testing_type": "thesis",
            "currently_testing_id": str(test_thesis.id),
            "commitments": [{"text": "Test", "order": 1}]
        }
        resp = await client.post(f"/api/canvases/{canvas.id}/reviews", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == status.HTTP_201_CREATED

    async def test_create_review_gm_own_canvas_only(self, client: AsyncClient, gm_token, own_canvas, other_canvas, test_thesis, other_canvas_thesis):
        """Test GM can only create review for own VBU canvas"""
        payload = {
            "review_date": str(date.today()), 
            "currently_testing_type": "thesis",
            "currently_testing_id": str(test_thesis.id),
            "commitments": [{"text": "Test", "order": 1}]
        }
        resp = await client.post(f"/api/canvases/{own_canvas.id}/reviews", json=payload, headers={"Authorization": f"Bearer {gm_token}"})
        assert resp.status_code == status.HTTP_201_CREATED
        
        payload_other = {
            "review_date": str(date.today()), 
            "currently_testing_type": "thesis",
            "currently_testing_id": str(other_canvas_thesis.id),
            "commitments": [{"text": "Test", "order": 1}]
        }
        resp_other = await client.post(f"/api/canvases/{other_canvas.id}/reviews", json=payload_other, headers={"Authorization": f"Bearer {gm_token}"})
        assert resp_other.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_review_viewer_forbidden(self, client: AsyncClient, viewer_token, canvas, test_thesis):
        """Test viewer cannot create reviews (403 Forbidden)"""
        payload = {
            "review_date": str(date.today()), 
            "currently_testing_type": "thesis",
            "currently_testing_id": str(test_thesis.id),
            "commitments": [{"text": "Test", "order": 1}]
        }
        resp = await client.post(f"/api/canvases/{canvas.id}/reviews", json=payload, headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_review_authorization_matrix(self, client: AsyncClient, admin_token, gm_token, viewer_token, review):
        """Test get single review follows same authorization as list"""
        resp_admin = await client.get(f"/api/reviews/{review.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp_admin.status_code == status.HTTP_200_OK
        resp_viewer = await client.get(f"/api/reviews/{review.id}", headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp_viewer.status_code == status.HTTP_200_OK

    async def test_unauthorized_access_returns_401(self, client: AsyncClient, canvas):
        """Test missing JWT returns 401 Unauthorized"""
        resp = await client.get(f"/api/canvases/{canvas.id}/reviews")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED