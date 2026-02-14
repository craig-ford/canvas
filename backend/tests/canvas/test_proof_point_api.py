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
    
    async def test_get_proof_points_success(self, client: AsyncClient, auth_headers: dict, sample_thesis: Thesis):
        """Test GET /api/theses/{thesis_id}/proof-points returns proof points with attachments"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        response = await client.get(f"/api/theses/{sample_thesis.id}/proof-points", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "meta" in data
        assert "total" in data["meta"]
    
    async def test_get_proof_points_unauthorized(self, client: AsyncClient, sample_thesis: Thesis):
        """Test GET without auth returns 401"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        response = await client.get(f"/api/theses/{sample_thesis.id}/proof-points")
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "UNAUTHORIZED"
    
    async def test_create_proof_point_success(self, client: AsyncClient, gm_auth_headers: dict, sample_thesis: Thesis):
        """Test POST /api/theses/{thesis_id}/proof-points creates proof point"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        proof_point_data = {
            "description": "Test proof point",
            "status": "not_started",
            "evidence_note": "Initial evidence",
            "target_review_month": "2026-03"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=gm_auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["description"] == "Test proof point"
        assert data["data"]["status"] == "not_started"
    
    async def test_create_proof_point_forbidden_viewer(self, client: AsyncClient, viewer_auth_headers: dict, sample_thesis: Thesis):
        """Test POST by viewer returns 403"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        proof_point_data = {
            "description": "Test proof point",
            "status": "not_started"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=viewer_auth_headers
        )
        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    async def test_create_proof_point_validation_error(self, client: AsyncClient, gm_auth_headers: dict, sample_thesis: Thesis):
        """Test POST with invalid data returns 422"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        proof_point_data = {
            "description": "",  # Empty description should fail
            "status": "invalid_status"
        }
        response = await client.post(
            f"/api/theses/{sample_thesis.id}/proof-points",
            json=proof_point_data,
            headers=gm_auth_headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
    
    async def test_update_proof_point_success(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test PATCH /api/proof-points/{id} updates proof point"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        update_data = {
            "description": "Updated proof point",
            "evidence_note": "Updated evidence"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=gm_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["description"] == "Updated proof point"
        assert data["data"]["evidence_note"] == "Updated evidence"
    
    async def test_update_proof_point_status_change(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test PATCH updates status from not_started to in_progress"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        update_data = {
            "status": "in_progress",
            "evidence_note": "Started working on this"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=gm_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "in_progress"
    
    async def test_update_proof_point_forbidden_other_gm(self, client: AsyncClient, other_gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test PATCH by different GM returns 403"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        update_data = {
            "description": "Unauthorized update"
        }
        response = await client.patch(
            f"/api/proof-points/{sample_proof_point.id}",
            json=update_data,
            headers=other_gm_auth_headers
        )
        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    async def test_delete_proof_point_success(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test DELETE /api/proof-points/{id} removes proof point"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        response = await client.delete(
            f"/api/proof-points/{sample_proof_point.id}",
            headers=gm_auth_headers
        )
        assert response.status_code == 204
    
    async def test_delete_proof_point_not_found(self, client: AsyncClient, gm_auth_headers: dict):
        """Test DELETE with invalid ID returns 404"""
        # BLOCKED: awaiting 002-canvas-management/T-017
        response = await client.delete(
            f"/api/proof-points/{uuid4()}",
            headers=gm_auth_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"


# Uses client and db fixtures from conftest.py


@pytest.fixture
async def auth_headers(db):
    """Create GM user and return auth headers."""
    auth_service = AuthService()
    user = await auth_service.register_user("gm@test.local", "password123", "GM User", "gm", db)
    token = await auth_service.create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def gm_auth_headers(db):
    """Create GM user and return auth headers."""
    auth_service = AuthService()
    user = await auth_service.register_user("gm1@test.local", "password123", "GM User 1", "gm", db)
    token = await auth_service.create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_gm_auth_headers(db):
    """Create different GM user and return auth headers."""
    auth_service = AuthService()
    user = await auth_service.register_user("gm2@test.local", "password123", "GM User 2", "gm", db)
    token = await auth_service.create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def viewer_auth_headers(db):
    """Create viewer user and return auth headers."""
    auth_service = AuthService()
    user = await auth_service.register_user("viewer@test.local", "password123", "Viewer User", "viewer", db)
    token = await auth_service.create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sample_thesis(db, gm_auth_headers):
    """Create sample thesis for testing."""
    auth_service = AuthService()
    canvas_service = CanvasService()
    
    # Get the GM user from the auth headers
    user = await auth_service.get_user_by_email("gm1@test.local", db)
    
    # Create VBU and get canvas
    vbu = await canvas_service.create_vbu("Test VBU", user.id, user.id, db)
    canvas = await canvas_service.get_canvas_by_vbu(vbu.id, db)
    
    # Create thesis
    thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db)
    return thesis


@pytest.fixture
async def sample_proof_point(db, sample_thesis):
    """Create sample proof point for testing."""
    canvas_service = CanvasService()
    proof_point = await canvas_service.create_proof_point(
        sample_thesis.id,
        "Test proof point",
        ProofPointStatus.NOT_STARTED.value,
        "Initial evidence",
        None,
        db
    )
    return proof_point