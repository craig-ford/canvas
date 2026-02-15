import pytest
from httpx import AsyncClient
from uuid import uuid4
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas


@pytest.mark.asyncio
async def test_get_portfolio_summary_admin_sees_all(client: AsyncClient, admin_user: User, admin_token: str, gm_user: User, db_session):
    """Admin can see all VBUs in portfolio summary"""
    vbu1 = VBU(name="VBU 1", gm_id=admin_user.id)
    vbu2 = VBU(name="VBU 2", gm_id=gm_user.id)
    db_session.add_all([vbu1, vbu2])
    await db_session.commit()

    canvas1 = Canvas(vbu_id=vbu1.id, lifecycle_lane="build", health_indicator_cache="On Track")
    canvas2 = Canvas(vbu_id=vbu2.id, lifecycle_lane="sell", health_indicator_cache="At Risk")
    db_session.add_all([canvas1, canvas2])
    await db_session.commit()

    response = await client.get("/api/portfolio/summary", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_get_portfolio_summary_gm_sees_own_only(client: AsyncClient, admin_user: User, gm_user: User, gm_token: str, db_session):
    """GM can only see their own VBUs"""
    vbu1 = VBU(name="Admin VBU", gm_id=admin_user.id)
    vbu2 = VBU(name="GM VBU", gm_id=gm_user.id)
    db_session.add_all([vbu1, vbu2])
    await db_session.commit()

    canvas1 = Canvas(vbu_id=vbu1.id, lifecycle_lane="build", health_indicator_cache="On Track")
    canvas2 = Canvas(vbu_id=vbu2.id, lifecycle_lane="sell", health_indicator_cache="At Risk")
    db_session.add_all([canvas1, canvas2])
    await db_session.commit()

    response = await client.get("/api/portfolio/summary", headers={"Authorization": f"Bearer {gm_token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "GM VBU"


@pytest.mark.asyncio
async def test_get_portfolio_summary_with_lane_filter(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """Filter portfolio summary by lifecycle lane"""
    vbu1 = VBU(name="Build VBU", gm_id=admin_user.id)
    vbu2 = VBU(name="Sell VBU", gm_id=admin_user.id)
    db_session.add_all([vbu1, vbu2])
    await db_session.commit()

    canvas1 = Canvas(vbu_id=vbu1.id, lifecycle_lane="build", health_indicator_cache="On Track")
    canvas2 = Canvas(vbu_id=vbu2.id, lifecycle_lane="sell", health_indicator_cache="At Risk")
    db_session.add_all([canvas1, canvas2])
    await db_session.commit()

    response = await client.get("/api/portfolio/summary?lane=build", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["lifecycle_lane"] == "build"


@pytest.mark.asyncio
async def test_get_portfolio_summary_with_health_filter(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """Filter portfolio summary by health status"""
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build", health_indicator_cache="At Risk")
    db_session.add(canvas)
    await db_session.commit()

    response = await client.get("/api/portfolio/summary?health_status=At Risk", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["health_indicator"] == "At Risk"


@pytest.mark.asyncio
async def test_get_portfolio_summary_invalid_lane_filter(client: AsyncClient, admin_token: str):
    """Invalid lane filter returns 422"""
    response = await client.get("/api/portfolio/summary?lane=invalid", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 422
    assert "Invalid lifecycle lane" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_get_portfolio_summary_invalid_health_filter(client: AsyncClient, admin_token: str):
    """Invalid health status filter returns 422"""
    response = await client.get("/api/portfolio/summary?health_status=Invalid", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 422
    assert "Invalid health status" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_get_portfolio_summary_invalid_gm_id_filter(client: AsyncClient, admin_token: str):
    """Invalid GM ID filter returns 422"""
    response = await client.get("/api/portfolio/summary?gm_id=invalid-uuid", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 422
    assert "Invalid GM ID format" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_update_portfolio_notes_admin_success(client: AsyncClient, admin_user: User, admin_token: str, db_session):
    """Admin can update portfolio notes"""
    vbu = VBU(name="Test VBU", gm_id=admin_user.id)
    db_session.add(vbu)
    await db_session.commit()

    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane="build")
    db_session.add(canvas)
    await db_session.commit()

    notes_data = {"notes": "Updated portfolio notes"}
    response = await client.patch("/api/portfolio/notes", json=notes_data, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["notes"] == "Updated portfolio notes"
    assert "updated_at" in data["data"]


@pytest.mark.asyncio
async def test_update_portfolio_notes_gm_forbidden(client: AsyncClient, gm_token: str):
    """GM cannot update portfolio notes"""
    notes_data = {"notes": "Should not work"}
    response = await client.patch("/api/portfolio/notes", json=notes_data, headers={"Authorization": f"Bearer {gm_token}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_portfolio_notes_viewer_forbidden(client: AsyncClient, viewer_token: str):
    """Viewer cannot update portfolio notes"""
    notes_data = {"notes": "Should not work"}
    response = await client.patch("/api/portfolio/notes", json=notes_data, headers={"Authorization": f"Bearer {viewer_token}"})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_portfolio_notes_too_long(client: AsyncClient, admin_token: str):
    """Portfolio notes exceeding max length returns 422"""
    notes_data = {"notes": "x" * 10001}
    response = await client.patch("/api/portfolio/notes", json=notes_data, headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_portfolio_summary_unauthorized(client: AsyncClient):
    """Unauthorized request returns 401"""
    response = await client.get("/api/portfolio/summary")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_portfolio_notes_unauthorized(client: AsyncClient):
    """Unauthorized request returns 401"""
    response = await client.patch("/api/portfolio/notes", json={"notes": "test"})
    assert response.status_code in (401, 403)
