import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from canvas.db import get_db_session, create_async_engine


def test_get_db_session_exists():
    """Test get_db_session function exists"""
    assert callable(get_db_session)


def test_get_db_session_returns_generator():
    """Test get_db_session returns AsyncGenerator"""
    result = get_db_session()
    assert hasattr(result, '__aiter__')
    assert hasattr(result, '__anext__')


@pytest.mark.asyncio
async def test_get_db_session_yields_session():
    """Test get_db_session yields AsyncSession instance"""
    async for session in get_db_session():
        assert isinstance(session, AsyncSession)
        break


def test_create_async_engine_exists():
    """Test create_async_engine function exists"""
    assert callable(create_async_engine)


def test_create_async_engine_returns_engine():
    """Test create_async_engine returns AsyncEngine"""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test")
    assert isinstance(engine, AsyncEngine)


@pytest.mark.asyncio
async def test_session_can_execute_query():
    """Test async session can execute simple query"""
    async for session in get_db_session():
        result = await session.execute("SELECT 1")
        assert result.scalar() == 1
        break


@pytest.mark.asyncio
async def test_session_cleanup():
    """Test session closes properly"""
    session_ref = None
    async for session in get_db_session():
        session_ref = session
        assert not session.is_active or session.in_transaction()
        break
    
    # Session should be closed after generator exits
    assert session_ref.is_active is False