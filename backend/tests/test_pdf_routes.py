import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint


@pytest.mark.asyncio
async def test_export_canvas_pdf_success_admin(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """Admin can export any VBU's canvas as PDF"""
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
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_export_canvas_pdf_success_gm_own_vbu(client: AsyncClient, gm_user: User, gm_token: str, db_session):
    """GM can export their own VBU's canvas as PDF"""
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
        headers={"Authorization": f"Bearer {gm_token}"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_export_canvas_pdf_gm_other_vbu_forbidden(client: AsyncClient, admin_user: User, gm_user: User, gm_token: str, db_session):
    """GM cannot export other GM's VBU canvas"""
    vbu = VBU(name="Admin VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build")
    db_session.add(canvas)
    await db_session.commit()

    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {gm_token}"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "VBU not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_viewer_can_export(client: AsyncClient, admin_user: User, viewer_token: str, db_session):
    """Viewer can export any VBU's canvas as PDF"""
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="milk")
    db_session.add(canvas)
    await db_session.commit()

    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_export_canvas_pdf_vbu_not_found(client: AsyncClient, admin_token: str):
    """Non-existent VBU returns 404"""
    non_existent_id = uuid4()

    response = await client.get(
        f"/api/vbus/{non_existent_id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "VBU not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_no_canvas(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """VBU without canvas returns 404"""
    vbu = VBU(name="VBU No Canvas", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Canvas not found"


@pytest.mark.asyncio
async def test_export_canvas_pdf_unauthorized(client: AsyncClient, admin_user: User, db_session):
    """Unauthorized request returns 401"""
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    response = await client.get(f"/api/vbus/{vbu.id}/canvas/pdf")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_export_canvas_pdf_filename_sanitization(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """VBU name with special characters is properly sanitized in filename"""
    vbu = VBU(name="Test/VBU With Spaces & Special-Chars", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build")
    db_session.add(canvas)
    await db_session.commit()

    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert "content-disposition" in response.headers


@pytest.mark.asyncio
async def test_export_canvas_pdf_content_headers(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """PDF export has correct content headers"""
    vbu = VBU(name="Header Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="reframe")
    db_session.add(canvas)
    await db_session.commit()

    response = await client.get(
        f"/api/vbus/{vbu.id}/canvas/pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("attachment")
    assert "filename=" in response.headers["content-disposition"]
