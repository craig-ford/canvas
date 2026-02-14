import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import date, timedelta

class TestCommitmentValidation:
    async def test_create_review_requires_1_to_3_commitments(self, client: AsyncClient, gm_token, canvas):
        """Test commitment count validation (1-3 required)"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload_zero = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": []}
        resp = await client.post("/api/reviews", json=payload_zero, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        payload_four = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": f"c{i}", "order": i} for i in range(1, 5)]}
        resp = await client.post("/api/reviews", json=payload_four, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_commitment_text_length_validation(self, client: AsyncClient, gm_token, canvas):
        """Test commitment text must be 1-1000 characters"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload_empty = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "", "order": 1}]}
        resp = await client.post("/api/reviews", json=payload_empty, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        payload_long = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "x" * 1001, "order": 1}]}
        resp = await client.post("/api/reviews", json=payload_long, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_commitment_order_uniqueness(self, client: AsyncClient, gm_token, canvas):
        """Test commitment orders must be unique within review"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "c1", "order": 1}, {"text": "c2", "order": 1}]}
        resp = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_commitment_order_range_validation(self, client: AsyncClient, gm_token, canvas):
        """Test commitment order must be 1-3"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "c1", "order": 0}]}
        resp = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        payload_high = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "c1", "order": 4}]}
        resp = await client.post("/api/reviews", json=payload_high, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_review_date_not_future(self, client: AsyncClient, gm_token, canvas):
        """Test review_date cannot be in the future"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        future_date = str(date.today() + timedelta(days=1))
        payload = {"canvas_id": str(canvas.id), "review_date": future_date, "commitments": [{"text": "c1", "order": 1}]}
        resp = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_currently_testing_validation(self, client: AsyncClient, gm_token, canvas, other_canvas_thesis):
        """Test currently_testing_id must belong to canvas"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "currently_testing_type": "thesis", "currently_testing_id": str(other_canvas_thesis.id), "commitments": [{"text": "c1", "order": 1}]}
        resp = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def test_text_field_length_limits(self, client: AsyncClient, gm_token, canvas):
        """Test what_moved/learned/threatens max 5000 chars"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "what_moved": "x" * 5001, "commitments": [{"text": "c1", "order": 1}]}
        resp = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_duplicate_review_date_conflict(self, client: AsyncClient, gm_token, canvas):
        """Test cannot create two reviews for same canvas and date"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        payload = {"canvas_id": str(canvas.id), "review_date": str(date.today()), "commitments": [{"text": "c1", "order": 1}]}
        resp1 = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp1.status_code == status.HTTP_201_CREATED
        resp2 = await client.post("/api/reviews", json=payload, headers=headers)
        assert resp2.status_code == status.HTTP_409_CONFLICT