import pytest
import asyncpg
from sqlalchemy import text


@pytest.mark.asyncio
async def test_postgres_accepts_connections():
    """Test PostgreSQL accepts connections on port 5432"""
    conn = await asyncpg.connect(
        user="canvas", password="canvas_dev", database="canvas_test", host="db", port=5432
    )
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_postgres_executes_queries():
    """Test database can execute simple queries"""
    conn = await asyncpg.connect(
        user="canvas", password="canvas_dev", database="canvas_test", host="db", port=5432
    )
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_backend_connects_to_db(db_session):
    """Test backend can connect to database via SQLAlchemy session."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
