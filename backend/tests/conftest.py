import os
import uuid

import pytest
import pytest_asyncio

# Set test environment BEFORE any app imports
os.environ["CANVAS_DATABASE_URL"] = "postgresql+asyncpg://canvas:canvas_dev@db:5432/canvas_test"
os.environ.setdefault("CANVAS_CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("CANVAS_SECRET_KEY", "test-secret-key-not-for-production")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport

from canvas.models import Base
from canvas.models.user import User, UserRole
from canvas.models.vbu import VBU
from canvas.models.canvas import Canvas, LifecycleLane
from canvas.models.monthly_review import MonthlyReview
from canvas.models.commitment import Commitment
from canvas.main import create_app
from canvas.db import get_db_session
from canvas.auth.service import AuthService

TEST_DB_URL = os.environ["CANVAS_DATABASE_URL"]

_schema_initialized = False


@pytest_asyncio.fixture
async def engine():
    """Create test database engine, initialize schema from models."""
    global _schema_initialized
    eng = create_async_engine(TEST_DB_URL, echo=False)

    if not _schema_initialized:
        async with eng.begin() as conn:
            # Drop everything from previous schema versions
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
            await conn.run_sync(Base.metadata.create_all)
        _schema_initialized = True

    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Create a test database session with cleanup after each test."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

    # Truncate all data between tests
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest_asyncio.fixture
async def db(db_session):
    """Alias for db_session."""
    return db_session


@pytest.fixture
def app(engine):
    """Create test application with overridden DB dependency."""
    application = create_app()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    application.dependency_overrides[get_db_session] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# --- Auth fixtures ---

@pytest.fixture
def auth_service():
    """Create AuthService instance for tests."""
    return AuthService()


@pytest.fixture
def user_service(auth_service):
    """Alias for auth_service."""
    return auth_service


@pytest_asyncio.fixture
async def admin_user(db_session, auth_service):
    """Create an admin user in the test database."""
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
    """Create a GM user in the test database."""
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
async def viewer_user(db_session, auth_service):
    """Create a viewer user in the test database."""
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
async def admin_token(admin_user, auth_service):
    """Create a JWT token for the admin user."""
    return await auth_service.create_access_token(admin_user)


@pytest_asyncio.fixture
async def gm_token(gm_user, auth_service):
    """Create a JWT token for the GM user."""
    return await auth_service.create_access_token(gm_user)


@pytest_asyncio.fixture
async def viewer_token(viewer_user, auth_service):
    """Create a JWT token for the viewer user."""
    return await auth_service.create_access_token(viewer_user)


@pytest_asyncio.fixture
async def authed_client(app, admin_token):
    """Create an authenticated async test client (admin)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as c:
        yield c


# --- Data fixtures ---

@pytest_asyncio.fixture
async def sample_vbu(db_session, gm_user):
    """Create a sample VBU."""
    vbu = VBU(id=uuid.uuid4(), name="Test VBU", gm_id=gm_user.id)
    db_session.add(vbu)
    await db_session.commit()
    await db_session.refresh(vbu)
    return vbu


@pytest_asyncio.fixture
async def sample_canvas(db_session, sample_vbu):
    """Create a sample Canvas linked to sample_vbu."""
    canvas = Canvas(
        id=uuid.uuid4(),
        vbu_id=sample_vbu.id,
        product_name="Test Product",
        lifecycle_lane=LifecycleLane.BUILD,
    )
    db_session.add(canvas)
    await db_session.commit()
    await db_session.refresh(canvas)
    return canvas


@pytest_asyncio.fixture
async def sample_review(db_session, sample_canvas, admin_user):
    """Create a sample MonthlyReview."""
    from datetime import date

    review = MonthlyReview(
        id=uuid.uuid4(),
        canvas_id=sample_canvas.id,
        review_date=date(2026, 1, 15),
        created_by=admin_user.id,
    )
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)
    return review
