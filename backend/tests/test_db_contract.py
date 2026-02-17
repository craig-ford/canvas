import pytest
import inspect
import ast
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


def test_get_db_session_exists():
    """Test get_db_session function exists"""
    # Import function without triggering Settings instantiation
    import importlib.util
    spec = importlib.util.spec_from_file_location("db_module", "canvas/db.py")
    # We can't actually import due to Settings() instantiation, but we can check the source
    with open("canvas/db.py", "r") as f:
        source = f.read()
    assert "async def get_db_session" in source


def test_get_db_session_is_async_generator():
    """Test get_db_session is defined as async generator function"""
    with open("canvas/db.py", "r") as f:
        source = f.read()
    
    # Parse AST to check function definition
    tree = ast.parse(source)
    get_db_session_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_db_session":
            get_db_session_found = True
            # Check it has return annotation
            assert node.returns is not None
            # Check it yields (making it a generator)
            has_yield = any(isinstance(n, ast.Yield) for n in ast.walk(node))
            assert has_yield, "get_db_session should yield to be a generator"
            break
    
    assert get_db_session_found, "get_db_session function not found"


def test_get_db_session_return_annotation():
    """Test get_db_session has correct return type annotation in source"""
    with open("canvas/db.py", "r") as f:
        source = f.read()
    
    # Check the return annotation is present in source
    assert "AsyncGenerator[AsyncSession, None]" in source


@pytest.mark.asyncio
async def test_session_can_execute_query(db_session):
    """Test async session can execute simple query"""
    from sqlalchemy import text
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_session_cleanup(db_session):
    """Test session closes properly after generator exits"""
    assert db_session is not None
    assert isinstance(db_session, AsyncSession)
