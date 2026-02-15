import pytest
import pytest_asyncio
import io
from uuid import uuid4
from httpx import AsyncClient


class TestAttachmentAPI:
    """Integration tests for /api/attachments endpoints."""

    @pytest.mark.asyncio
    async def test_download_file_not_found(self, authed_client: AsyncClient):
        """GET /api/attachments/{id} with invalid UUID returns 404."""
        fake_id = uuid4()
        response = await authed_client.get(f"/api/attachments/{fake_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_download_file_invalid_uuid(self, authed_client: AsyncClient):
        """GET /api/attachments/not-a-uuid returns 422."""
        response = await authed_client.get("/api/attachments/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_requires_auth(self, client: AsyncClient):
        """POST /api/attachments without auth returns 401 (no bearer)."""
        file_content = b'\x89PNG\r\n\x1a\n'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        data = {"proof_point_id": str(uuid4())}
        response = await client.post("/api/attachments", files=files, data=data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_missing_parent_id(self, authed_client: AsyncClient):
        """POST /api/attachments without proof_point_id or monthly_review_id returns 422."""
        file_content = b'\x89PNG\r\n\x1a\n'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        response = await authed_client.post("/api/attachments", files=files)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_upload_nonexistent_proof_point(self, authed_client: AsyncClient):
        """POST /api/attachments with nonexistent proof_point_id returns 404."""
        file_content = b'\x89PNG\r\n\x1a\n'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        data = {"proof_point_id": str(uuid4())}
        response = await authed_client.post("/api/attachments", files=files, data=data)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_delete_not_found(self, authed_client: AsyncClient):
        """DELETE /api/attachments/{id} with invalid UUID returns 404."""
        fake_id = uuid4()
        response = await authed_client.delete(f"/api/attachments/{fake_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
