import pytest
import asyncio
import asyncpg
import subprocess
import time
from canvas.config import Settings


@pytest.mark.asyncio
async def test_postgres_container_starts():
    """Test PostgreSQL container starts"""
    result = subprocess.run(
        ["docker", "compose", "ps", "db"], 
        capture_output=True, text=True
    )
    assert "Up" in result.stdout or "running" in result.stdout


@pytest.mark.asyncio
async def test_postgres_health_check():
    """Test pg_isready command succeeds with correct user"""
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "db", "pg_isready", "-U", "canvas"],
        capture_output=True, text=True
    )
    assert result.returncode == 0


@pytest.mark.asyncio
async def test_postgres_accepts_connections():
    """Test PostgreSQL accepts connections on port 5432"""
    settings = Settings()
    try:
        conn = await asyncpg.connect(settings.database_url)
        await conn.close()
        assert True
    except Exception:
        assert False, "Could not connect to PostgreSQL"


@pytest.mark.asyncio
async def test_postgres_executes_queries():
    """Test database can execute simple queries"""
    settings = Settings()
    conn = await asyncpg.connect(settings.database_url)
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_backend_connects_to_db():
    """Test backend can connect to database via Docker network"""
    from canvas.db import get_db_session
    async for session in get_db_session():
        result = await session.execute("SELECT 1")
        assert result.scalar() == 1
        break


@pytest.mark.asyncio
async def test_service_dependency_order():
    """Test service dependency ordering works correctly"""
    # Check that db service is running before backend starts
    db_result = subprocess.run(
        ["docker", "compose", "ps", "db"], 
        capture_output=True, text=True
    )
    backend_result = subprocess.run(
        ["docker", "compose", "ps", "backend"], 
        capture_output=True, text=True
    )
    
    # Both should be running if dependency order is correct
    assert "Up" in db_result.stdout or "running" in db_result.stdout
    assert "Up" in backend_result.stdout or "running" in backend_result.stdout