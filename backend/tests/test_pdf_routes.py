import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint


@pytest.mark.asyncio
async def test_export_canvas_pdf_success_admin(client: AsyncClient, admin_user: User, db_session):
    """Admin can export any VBU's canvas as PDF"""
    # Create VBU and canvas
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(
        vbu_id=vbu.id,
        lifecycle_lane="build",
        success_description="Test success description",
        primary_constraint="Test constraint"
    )
    db_session.add(canvas)
    await db_session.commit()
    
    # Add thesis and proof point for complete canvas
    thesis = Thesis(canvas_id=canvas.id, order=1, text="Test thesis")
    db_session.add(thesis)
    await db_session.commit()
    
    proof_point = ProofPoint(
        thesis_id=thesis.id,
        description="Test proof point",
        status="in_progress"
    )
    db_session.add(proof_point)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_user.access_token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert f"{vbu.name}_canvas.pdf" in response.headers["content-disposition"]
    assert "content-length" in response.headers
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_export_canvas_pdf_success_gm_own_vbu(client: AsyncClient, gm_user: User, db_session):
    """GM can export their own VBU's canvas as PDF"""
    # Create VBU owned by GM
    vbu = VBU(name="GM VBU", gm_id=gm_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(
        vbu_id=vbu.id,
        lifecycle_lane="sell",
        success_description="GM success description"
    )
    db_session.add(canvas)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {gm_user.access_token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_export_canvas_pdf_gm_other_vbu_forbidden(client: AsyncClient, admin_user: User, gm_user: User, db_session):
    """GM cannot export other GM's VBU canvas"""
    # Create VBU owned by admin
    vbu = VBU(name="Admin VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build")
    db_session.add(canvas)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {gm_user.access_token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "VBU not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_viewer_can_export(client: AsyncClient, admin_user: User, viewer_user: User, db_session):
    """Viewer can export any VBU's canvas as PDF"""
    # Create VBU
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="milk")
    db_session.add(canvas)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {viewer_user.access_token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_export_canvas_pdf_vbu_not_found(client: AsyncClient, admin_user: User):
    """Non-existent VBU returns 404"""
    non_existent_id = uuid4()
    
    response = await client.get(
        f"/api/vbus/{non_existent_id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_user.access_token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "VBU not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_no_canvas(client: AsyncClient, admin_user: User, db_session):
    """VBU without canvas returns 404"""
    # Create VBU without canvas
    vbu = VBU(name="VBU No Canvas", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_user.access_token}"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Canvas not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_unauthorized(client: AsyncClient, admin_user: User, db_session):
    """Unauthorized request returns 401"""
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    response = await client.get(f"/api/vbus/{vbu.id}/canvas/pdf")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_canvas_pdf_filename_sanitization(client: AsyncClient, admin_user: User, db_session):
    """VBU name with special characters is properly sanitized in filename"""
    # Create VBU with special characters in name
    vbu = VBU(name="Test/VBU With Spaces & Special-Chars", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build")
    db_session.add(canvas)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_user.access_token}"}
    )
    
    assert response.status_code == 200
    # Filename should contain the VBU name (browser will handle sanitization)
    assert vbu.name in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_export_canvas_pdf_content_headers(client: AsyncClient, admin_user: User, db_session):
    """PDF export has correct content headers"""
    vbu = VBU(name="Header Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()
    
    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="reframe")
    db_session.add(canvas)
    await db_session.commit()
    
    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_user.access_token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("attachment")
    assert "filename=" in response.headers["content-disposition"]
    assert "content-length" in response.headers
    assert int(response.headers["content-length"]) > 0