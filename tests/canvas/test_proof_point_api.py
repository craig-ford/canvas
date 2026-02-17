import pytest
from uuid import uuid4
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint, ProofPointStatus
from canvas.auth.service import AuthService
from canvas.services.canvas_service import CanvasService


class TestProofPointAPI:
    """Integration tests for proof point CRUD endpoints"""
    
    async def test_get_proof_points_success(self, client: AsyncClient, gm_token: str, sample_thesis: Thesis):
        """Test GET /api/theses/{thesis_id}/proof-points returns proof points with attachments"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        response = await client.get(f"/api/theses/{sample_thesis.id}/proof-points", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "meta" in data
        assert "total" in data["meta"]
    
    async def test_get_proof_points_unauthorized(self, client: AsyncClient, sample_thesis: Thesis):
        """Test GET without auth returns 401"""
        response = await client.get(f"/api/theses/{sample_thesis.id}/proof-points")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
    
    async def test_create_proof_point_success(self, client: AsyncClient, gm_token: str, sample_thesis: Thesis):
        """Test POST /api/theses/{thesis_id}/proof-points creates proof point"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        proof_point_data = {
            "description": "Test proof point",
            "status": "not_started",
            "evidence_note": "Initial evidence",
            "target_review_month": "2026-03"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["description"] == "Test proof point"
        assert data["data"]["status"] == "not_started"
    
    async def test_create_proof_point_forbidden_viewer(self, client: AsyncClient, viewer_token: str, sample_thesis: Thesis):
        """Test POST by viewer returns 403"""
        headers = {"Authorization": f"Bearer {viewer_token}"}
        proof_point_data = {
            "description": "Test proof point",
            "status": "not_started"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=headers
        )
        assert response.status_code == 403
        data = response.json()
        assert "error" in data
    
    async def test_create_proof_point_validation_error(self, client: AsyncClient, gm_token: str, sample_thesis: Thesis):
        """Test POST with invalid data returns 422"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        proof_point_data = {
            "description": "",  # Empty description should fail
            "status": "invalid_status"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_update_proof_point_success(self, client: AsyncClient, gm_token: str, sample_proof_point: ProofPoint):
        """Test PATCH /api/proof-points/{id} updates proof point"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        update_data = {
            "description": "Updated proof point",
            "evidence_note": "Updated evidence"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["description"] == "Updated proof point"
        assert data["data"]["evidence_note"] == "Updated evidence"
    
    async def test_update_proof_point_status_change(self, client: AsyncClient, gm_token: str, sample_proof_point: ProofPoint):
        """Test PATCH updates status from not_started to in_progress"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        update_data = {
            "status": "in_progress",
            "evidence_note": "Started working on this"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "in_progress"
    
    async def test_update_proof_point_forbidden_other_gm(self, client: AsyncClient, other_gm_token: str, sample_proof_point: ProofPoint):
        """Test PATCH by different GM returns 403"""
        headers = {"Authorization": f"Bearer {other_gm_token}"}
        update_data = {
            "description": "Unauthorized update"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 403
        data = response.json()
        assert "error" in data
    
    async def test_delete_proof_point_success(self, client: AsyncClient, gm_token: str, sample_proof_point: ProofPoint):
        """Test DELETE /api/proof-points/{id} removes proof point"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        response = await client.delete(
            f"/api/proof-points/{sample_proof_point.id}",
            headers=headers
        )
        assert response.status_code == 204
    
    async def test_delete_proof_point_not_found(self, client: AsyncClient, gm_token: str):
        """Test DELETE with invalid ID returns 404"""
        headers = {"Authorization": f"Bearer {gm_token}"}
        response = await client.delete(
            f"/api/proof-points/{uuid4()}",
            headers=headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


# Uses client and db fixtures from conftest.py


@pytest.fixture
async def sample_proof_point(db_session, sample_thesis):
    """Create sample proof point for testing."""
    proof_point = ProofPoint(
        id=uuid4(),
        thesis_id=sample_thesis.id,
        description="Test proof point",
        status=ProofPointStatus.NOT_STARTED,
        evidence_note="Initial evidence"
    )
    db_session.add(proof_point)
    await db_session.commit()
    await db_session.refresh(proof_point)
    return proof_point