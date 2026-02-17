import os
import uuid
from datetime import date

import pytest
import pytest_asyncio

# Set test environment BEFORE any app imports
os.environ["CANVAS_DATABASE_URL"] = "postgresql+asyncpg://canvas:canvas_dev@db:5432/canvas_test"
os.environ.setdefault("CANVAS_CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("CANVAS_SECRET_KEY", "test-secret-key-not-for-production")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import text, event, select, create_engine
from httpx import AsyncClient, ASGITransport

from canvas.models import Base
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane
from canvas.models.thesis import Thesis
from canvas.models.proof_point import ProofPoint, ProofPointStatus
from canvas.models.monthly_review import MonthlyReview
from canvas.models.commitment import Commitment
from canvas.main import create_app
from canvas.db import get_db_session
from canvas.auth.service import AuthService
from canvas.auth.user_service import UserService

TEST_DB_URL = os.environ["CANVAS_DATABASE_URL"]
SYNC_DB_URL = TEST_DB_URL.replace("+asyncpg", "")

# --- Schema setup ONCE at import time using sync engine (no event loop issues) ---
_sync_engine = create_engine(SYNC_DB_URL)
Base.metadata.drop_all(_sync_engine)
Base.metadata.create_all(_sync_engine)
_sync_engine.dispose()


@pytest_asyncio.fixture
async def _engine():
    """Per-test async engine with NullPool."""
    eng = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def engine(_engine):
    """Public engine fixture."""
    return _engine


@pytest_asyncio.fixture
async def _connection(_engine):
    """Per-test connection with outer transaction for rollback isolation."""
    async with _engine.connect() as conn:
        trans = await conn.begin()
        yield conn
        await trans.rollback()


@pytest_asyncio.fixture
async def db_session(_connection):
    """Test session using savepoints so commit() doesn't kill the outer transaction."""
    session = AsyncSession(bind=_connection, expire_on_commit=False)

    @event.listens_for(session.sync_session, "after_transaction_end")
    def restart_savepoint(sess, transaction):
        if transaction.nested and not transaction._parent.nested:
            sess.begin_nested()

    await session.begin_nested()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def db(db_session):
    """Alias for db_session."""
    return db_session


@pytest.fixture
def app(_connection):
    """Create test application sharing the same connection/transaction."""
    application = create_app()

    async def override_get_db():
        session = AsyncSession(bind=_connection, expire_on_commit=False)
        await session.begin_nested()
        try:
            yield session
        finally:
            await session.close()

    application.dependency_overrides[get_db_session] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app):
    """Create async test client with Origin header for CSRF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Origin": "http://localhost:3000"},
    ) as c:
        yield c


# --- Service fixtures ---

@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
def user_service():
    return UserService()


# --- User fixtures ---

@pytest_asyncio.fixture
async def admin_user(db_session, auth_service):
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        password_hash=auth_service._hash_password("Admin123!"),
        name="Test Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def gm_user(db_session, auth_service):
    user = User(
        id=uuid.uuid4(),
        email="gm@test.com",
        password_hash=auth_service._hash_password("Gm12345!"),
        name="Test GM",
        role=UserRole.GM,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_gm_user(db_session, auth_service):
    user = User(
        id=uuid.uuid4(),
        email="othergm@test.com",
        password_hash=auth_service._hash_password("OtherGm1!"),
        name="Other GM",
        role=UserRole.GM,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def viewer_user(db_session, auth_service):
    user = User(
        id=uuid.uuid4(),
        email="viewer@test.com",
        password_hash=auth_service._hash_password("View123!"),
        name="Test Viewer",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_user(db_session, auth_service):
    user = User(
        id=uuid.uuid4(),
        email="sample@test.com",
        password_hash=auth_service._hash_password("Sample1!"),
        name="Sample User",
        role=UserRole.VIEWER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Token fixtures ---

@pytest_asyncio.fixture
async def admin_token(admin_user, auth_service):
    return await auth_service.create_access_token(admin_user)


@pytest_asyncio.fixture
async def gm_token(gm_user, auth_service):
    return await auth_service.create_access_token(gm_user)


@pytest_asyncio.fixture
async def other_gm_token(other_gm_user, auth_service):
    return await auth_service.create_access_token(other_gm_user)


@pytest_asyncio.fixture
async def viewer_token(viewer_user, auth_service):
    return await auth_service.create_access_token(viewer_user)


@pytest_asyncio.fixture
async def authed_client(app, admin_token):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Origin": "http://localhost:3000",
        },
    ) as c:
        yield c


# --- VBU fixtures ---

@pytest_asyncio.fixture
async def sample_vbu(db_session, gm_user):
    vbu = VBU(id=uuid.uuid4(), name="Test VBU", gm_id=gm_user.id)
    db_session.add(vbu)
    await db_session.flush()
    canvas = Canvas(
        id=uuid.uuid4(),
        vbu_id=vbu.id,
        product_name="Test Product",
        lifecycle_lane=LifecycleLane.BUILD,
    )
    db_session.add(canvas)
    await db_session.commit()
    await db_session.refresh(vbu)
    return vbu


@pytest_asyncio.fixture
async def test_vbu(sample_vbu):
    return sample_vbu


@pytest_asyncio.fixture
async def gm_vbu(sample_vbu):
    return sample_vbu


@pytest_asyncio.fixture
async def other_vbu(db_session, other_gm_user):
    vbu = VBU(id=uuid.uuid4(), name="Other VBU", gm_id=other_gm_user.id)
    db_session.add(vbu)
    await db_session.flush()
    canvas = Canvas(
        id=uuid.uuid4(),
        vbu_id=vbu.id,
        product_name="Other Product",
        lifecycle_lane=LifecycleLane.SELL,
    )
    db_session.add(canvas)
    await db_session.commit()
    await db_session.refresh(vbu)
    return vbu


# --- Canvas fixtures ---

@pytest_asyncio.fixture
async def sample_canvas(db_session, sample_vbu):
    result = await db_session.execute(
        select(Canvas).where(Canvas.vbu_id == sample_vbu.id)
    )
    return result.scalar_one()


@pytest_asyncio.fixture
async def test_canvas(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def canvas(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def gm_canvas(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def any_canvas(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def canvas_a(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def own_canvas(sample_canvas):
    return sample_canvas


@pytest_asyncio.fixture
async def other_canvas(db_session, other_vbu):
    result = await db_session.execute(
        select(Canvas).where(Canvas.vbu_id == other_vbu.id)
    )
    return result.scalar_one()


# --- Thesis fixtures ---

@pytest_asyncio.fixture
async def sample_thesis(db_session, sample_canvas):
    thesis = Thesis(
        id=uuid.uuid4(),
        canvas_id=sample_canvas.id,
        order=1,
        text="Test thesis statement",
    )
    db_session.add(thesis)
    await db_session.commit()
    await db_session.refresh(thesis)
    return thesis


@pytest_asyncio.fixture
async def test_thesis(sample_thesis):
    return sample_thesis


@pytest_asyncio.fixture
async def gm_thesis(sample_thesis):
    return sample_thesis


@pytest_asyncio.fixture
async def sample_proof_point(db_session, sample_thesis):
    pp = ProofPoint(
        id=uuid.uuid4(),
        thesis_id=sample_thesis.id,
        description="Test proof point",
        status=ProofPointStatus.NOT_STARTED,
    )
    db_session.add(pp)
    await db_session.commit()
    await db_session.refresh(pp)
    return pp


@pytest_asyncio.fixture
async def other_canvas_thesis(db_session, other_canvas):
    thesis = Thesis(
        id=uuid.uuid4(),
        canvas_id=other_canvas.id,
        order=1,
        text="Other canvas thesis",
    )
    db_session.add(thesis)
    await db_session.commit()
    await db_session.refresh(thesis)
    return thesis


@pytest_asyncio.fixture
async def canvas_with_theses(db_session, sample_canvas):
    for i in range(1, 4):
        thesis = Thesis(
            id=uuid.uuid4(),
            canvas_id=sample_canvas.id,
            order=i,
            text=f"Thesis {i}",
        )
        db_session.add(thesis)
    await db_session.commit()
    await db_session.refresh(sample_canvas, ["theses"])
    return sample_canvas


@pytest_asyncio.fixture
async def canvas_with_multiple_theses(canvas_with_theses):
    return canvas_with_theses


@pytest_asyncio.fixture
async def other_canvas_with_theses(db_session, other_canvas):
    for i in range(1, 3):
        thesis = Thesis(
            id=uuid.uuid4(),
            canvas_id=other_canvas.id,
            order=i,
            text=f"Other thesis {i}",
        )
        db_session.add(thesis)
    await db_session.commit()
    await db_session.refresh(other_canvas, ["theses"])
    return other_canvas


@pytest_asyncio.fixture
async def canvas_with_proof_points(db_session, sample_canvas):
    thesis = Thesis(
        id=uuid.uuid4(),
        canvas_id=sample_canvas.id,
        order=1,
        text="Thesis with proof points",
    )
    db_session.add(thesis)
    await db_session.flush()
    pp = ProofPoint(
        id=uuid.uuid4(),
        thesis_id=thesis.id,
        description="Test proof point",
        status=ProofPointStatus.NOT_STARTED,
    )
    db_session.add(pp)
    await db_session.commit()
    await db_session.refresh(sample_canvas, ["theses"])
    return sample_canvas


@pytest_asyncio.fixture
async def canvas_with_thesis(canvas_with_theses):
    return canvas_with_theses


# --- Review fixtures ---

@pytest_asyncio.fixture
async def sample_review(db_session, sample_canvas, admin_user):
    review = MonthlyReview(
        id=uuid.uuid4(),
        canvas_id=sample_canvas.id,
        review_date=date(2026, 1, 15),
        created_by=admin_user.id,
    )
    db_session.add(review)
    await db_session.flush()
    commitment = Commitment(
        id=uuid.uuid4(),
        monthly_review_id=review.id,
        text="Test commitment",
        order=1,
    )
    db_session.add(commitment)
    await db_session.commit()
    await db_session.refresh(review, ["commitments"])
    return review


@pytest_asyncio.fixture
async def review(sample_review):
    return sample_review


@pytest_asyncio.fixture
async def canvas_b(other_canvas):
    return other_canvas
