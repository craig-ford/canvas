import pytest
import tempfile
from pathlib import Path
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.proof_point import ProofPoint
from canvas.models.attachment import Attachment
from canvas.auth.service import AuthService
from canvas.services.canvas_service import CanvasService
from canvas.services.attachment_service import AttachmentService
import io


class TestAttachmentAPI:
    """Integration tests for file upload/download endpoints"""
    
    async def test_upload_file_success(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test POST /api/attachments uploads file with multipart form data"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        data = {
            "proof_point_id": str(sample_proof_point.id),
            "label": "Test image"
        }
        
        response = await client.post("/api/attachments", files=files, data=data, headers=gm_auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert "data" in result
        assert result["data"]["filename"] == "test.png"
        assert result["data"]["content_type"] == "image/png"
        assert result["data"]["label"] == "Test image"
    
    async def test_upload_file_unauthorized(self, client: AsyncClient, sample_proof_point: ProofPoint):
        """Test POST without auth returns 401"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        data = {"proof_point_id": str(sample_proof_point.id)}
        
        response = await client.post("/api/attachments", files=files, data=data)
        assert response.status_code == 401
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "UNAUTHORIZED"
    
    async def test_upload_file_forbidden_viewer(self, client: AsyncClient, viewer_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test POST by viewer returns 403"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
        data = {"proof_point_id": str(sample_proof_point.id)}
        
        response = await client.post("/api/attachments", files=files, data=data, headers=viewer_auth_headers)
        assert response.status_code == 403
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "FORBIDDEN"
    
    async def test_upload_file_too_large(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test POST with file >10MB returns 413 FILE_TOO_LARGE"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        # Create file larger than 10MB
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
        data = {"proof_point_id": str(sample_proof_point.id)}
        
        response = await client.post("/api/attachments", files=files, data=data, headers=gm_auth_headers)
        assert response.status_code == 413
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "FILE_TOO_LARGE"
    
    async def test_upload_unsupported_type(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test POST with unsupported MIME type returns 415 UNSUPPORTED_TYPE"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        file_content = b'unsupported content'
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-executable")}
        data = {"proof_point_id": str(sample_proof_point.id)}
        
        response = await client.post("/api/attachments", files=files, data=data, headers=gm_auth_headers)
        assert response.status_code == 415
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "UNSUPPORTED_TYPE"
    
    async def test_upload_with_label(self, client: AsyncClient, gm_auth_headers: dict, sample_proof_point: ProofPoint):
        """Test POST with optional label field"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        files = {"file": ("labeled.png", io.BytesIO(file_content), "image/png")}
        data = {
            "proof_point_id": str(sample_proof_point.id),
            "label": "Custom Label"
        }
        
        response = await client.post("/api/attachments", files=files, data=data, headers=gm_auth_headers)
        assert response.status_code == 201
        result = response.json()
        assert "data" in result
        assert result["data"]["label"] == "Custom Label"
    
    async def test_download_file_success(self, client: AsyncClient, auth_headers: dict, sample_attachment: Attachment):
        """Test GET /api/attachments/{id} returns file with proper headers"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        response = await client.get(f"/api/attachments/{sample_attachment.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == sample_attachment.content_type
        assert "attachment" in response.headers.get("content-disposition", "")
        assert sample_attachment.filename in response.headers.get("content-disposition", "")
    
    async def test_download_file_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test GET with invalid ID returns 404"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        fake_id = uuid4()
        response = await client.get(f"/api/attachments/{fake_id}", headers=auth_headers)
        assert response.status_code == 404
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"
    
    async def test_download_file_forbidden_other_gm(self, client: AsyncClient, other_gm_auth_headers: dict, sample_attachment: Attachment):
        """Test GET by different GM returns 403"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        response = await client.get(f"/api/attachments/{sample_attachment.id}", headers=other_gm_auth_headers)
        assert response.status_code == 403
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "FORBIDDEN"
    
    async def test_delete_file_success(self, client: AsyncClient, gm_auth_headers: dict, sample_attachment: Attachment):
        """Test DELETE /api/attachments/{id} removes file and database record"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        response = await client.delete(f"/api/attachments/{sample_attachment.id}", headers=gm_auth_headers)
        assert response.status_code == 204
        
        # Verify file is deleted by trying to download
        download_response = await client.get(f"/api/attachments/{sample_attachment.id}", headers=gm_auth_headers)
        assert download_response.status_code == 404
    
    async def test_delete_file_forbidden_viewer(self, client: AsyncClient, viewer_auth_headers: dict, sample_attachment: Attachment):
        """Test DELETE by viewer returns 403"""
        # BLOCKED: awaiting 002-canvas-management/T-018
        response = await client.delete(f"/api/attachments/{sample_attachment.id}", headers=viewer_auth_headers)
        assert response.status_code == 403
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == "FORBIDDEN"


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
async def sample_proof_point(db, gm_auth_headers):
    """Create sample proof point for testing."""
    auth_service = AuthService()
    canvas_service = CanvasService()
    
    # Get the GM user from the auth headers
    user = await auth_service.get_user_by_email("gm1@test.local", db)
    
    # Create VBU and get canvas
    vbu = await canvas_service.create_vbu("Test VBU", user.id, user.id, db)
    canvas = await canvas_service.get_canvas_by_vbu(vbu.id, db)
    
    # Create thesis
    thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db)
    
    # Create proof point
    proof_point = await canvas_service.create_proof_point(
        thesis.id,
        "Test proof point",
        "not_started",
        "Initial evidence",
        None,
        db
    )
    return proof_point


@pytest.fixture
async def sample_attachment(db, sample_proof_point, gm_auth_headers):
    """Create sample attachment for testing."""
    auth_service = AuthService()
    attachment_service = AttachmentService()
    
    # Get the GM user
    user = await auth_service.get_user_by_email("gm1@test.local", db)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde')
        temp_file.flush()
        
        # Create attachment
        attachment = await attachment_service.upload(
            temp_file.name,
            sample_proof_point.id,
            None,
            user.id,
            db,
            "test.png",
            "image/png",
            len(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'),
            "Test attachment"
        )
        return attachment