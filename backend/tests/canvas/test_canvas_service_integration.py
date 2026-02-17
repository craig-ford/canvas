import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from canvas.services.canvas_service import CanvasService
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint, ProofPointStatus
from canvas.auth.service import AuthService

@pytest.fixture
def canvas_service():
    return CanvasService()

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    svc = AuthService()
    user = User(
        id=uuid4(),
        email="svc-gm@test.com",
        password_hash=svc._hash_password("Test1234!"),
        name="Test GM",
        role=UserRole.GM,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_vbu(db_session: AsyncSession, test_user: User):
    vbu = VBU(id=uuid4(), name="Test VBU", gm_id=test_user.id)
    db_session.add(vbu)
    await db_session.flush()
    # Auto-create canvas for this VBU (matches CanvasService.create_vbu behavior)
    canvas = Canvas(vbu_id=vbu.id, lifecycle_lane=LifecycleLane.BUILD, updated_by=test_user.id)
    db_session.add(canvas)
    await db_session.commit()
    await db_session.refresh(vbu)
    return vbu

class TestCanvasServiceVBU:
    async def test_create_vbu(self, canvas_service: CanvasService, test_user: User, db_session: AsyncSession):
        vbu = await canvas_service.create_vbu("New VBU", test_user.id, test_user.id, db_session)
        assert vbu.name == "New VBU"
        assert vbu.gm_id == test_user.id

    async def test_update_vbu(self, canvas_service: CanvasService, test_vbu: VBU, test_user: User, db_session: AsyncSession):
        updated_vbu = await canvas_service.update_vbu(test_vbu.id, "Updated Name", None, test_user.id, db_session)
        assert updated_vbu.name == "Updated Name"

    async def test_delete_vbu(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        await canvas_service.delete_vbu(test_vbu.id, db_session)
        result = await db_session.get(VBU, test_vbu.id)
        assert result is None

    async def test_list_vbus(self, canvas_service: CanvasService, test_user: User, db_session: AsyncSession):
        vbus = await canvas_service.list_vbus(test_user, db_session)
        assert isinstance(vbus, list)

class TestCanvasServiceCanvas:
    async def test_get_canvas_by_vbu(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        assert canvas.vbu_id == test_vbu.id

    async def test_update_canvas(self, canvas_service: CanvasService, test_vbu: VBU, test_user: User, db_session: AsyncSession):
        canvas_data = {"lifecycle_lane": LifecycleLane.SELL, "product_name": "Test Product"}
        canvas = await canvas_service.update_canvas(test_vbu.id, canvas_data, test_user.id, db_session)
        assert canvas.lifecycle_lane == LifecycleLane.SELL
        assert canvas.product_name == "Test Product"

class TestCanvasServiceThesis:
    async def test_create_thesis(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db_session)
        assert thesis.text == "Test thesis"
        assert thesis.order == 1

    async def test_update_thesis(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "Original", 1, db_session)
        updated = await canvas_service.update_thesis(thesis.id, "Updated", db_session)
        assert updated.text == "Updated"

    async def test_delete_thesis(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "To delete", 1, db_session)
        await canvas_service.delete_thesis(thesis.id, db_session)
        result = await db_session.get(Thesis, thesis.id)
        assert result is None

    async def test_reorder_theses(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        t1 = await canvas_service.create_thesis(canvas.id, "First", 1, db_session)
        t2 = await canvas_service.create_thesis(canvas.id, "Second", 2, db_session)
        # Swap the orders: t1 goes from 1->2, t2 goes from 2->1
        reordered = await canvas_service.reorder_theses(canvas.id, [{"id": str(t1.id), "order": 2}, {"id": str(t2.id), "order": 1}], db_session)
        assert len(reordered) == 2
        # Verify the reordering worked
        assert reordered[0].id == t2.id and reordered[0].order == 1
        assert reordered[1].id == t1.id and reordered[1].order == 2

class TestCanvasServiceProofPoint:
    async def test_create_proof_point(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db_session)
        pp = await canvas_service.create_proof_point(thesis.id, "Test proof point", ProofPointStatus.NOT_STARTED.value, None, None, db_session)
        assert pp.description == "Test proof point"
        assert pp.status == ProofPointStatus.NOT_STARTED

    async def test_update_proof_point(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db_session)
        pp = await canvas_service.create_proof_point(thesis.id, "Original", ProofPointStatus.NOT_STARTED.value, None, None, db_session)
        updated = await canvas_service.update_proof_point(pp.id, "Updated", ProofPointStatus.IN_PROGRESS.value, "Evidence", "2026-03", db_session)
        assert updated.description == "Updated"
        assert updated.status == ProofPointStatus.IN_PROGRESS

    async def test_delete_proof_point(self, canvas_service: CanvasService, test_vbu: VBU, db_session: AsyncSession):
        canvas = await canvas_service.get_canvas_by_vbu(test_vbu.id, db_session)
        thesis = await canvas_service.create_thesis(canvas.id, "Test thesis", 1, db_session)
        pp = await canvas_service.create_proof_point(thesis.id, "To delete", ProofPointStatus.NOT_STARTED.value, None, None, db_session)
        await canvas_service.delete_proof_point(pp.id, db_session)
        result = await db_session.get(ProofPoint, pp.id)
        assert result is None
