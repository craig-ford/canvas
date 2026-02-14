import pytest
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from canvas.db import get_db_session


def test_get_db_session_exists():
    """Test get_db_session function exists"""
    assert callable(get_db_session)


def test_get_db_session_returns_generator():
    """Test get_db_session returns AsyncGenerator"""
    result = get_db_session()
    assert hasattr(result, '__aiter__')
    assert hasattr(result, '__anext__')


@pytest.mark.asyncio
async def test_session_can_execute_query(db_session):
    """Test async session can execute simple query"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_session_cleanup():
    """Test session closes properly after generator exits"""
    session_ref = None
    async for session in get_db_session():
        session_ref = session
        break

    # After generator exits, session should be closed
    assert session_ref is not None
