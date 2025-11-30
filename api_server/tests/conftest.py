import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys
# Add the api_server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from server import app
from storage.wrappers.sql_wrapper import SQLWrapper

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_client():
    """Global test client fixture"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db_session():
    """Database session fixture with rollback"""
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def sql_wrapper(db_session):
    """SQL wrapper fixture"""
    return SQLWrapper(db_session)

@pytest.fixture(scope="session")
def event_loop():
    """Event loop fixture for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Sample data fixtures
@pytest.fixture
def sample_staff_data():
    return {
        "org_id": 1,
        "provider_id": 1,
        "user_id": 123,
        "rule_id": 1,
        "rule_name": "Test Manager",
        "rule_type": "manager",
        "is_active": True
    }

@pytest.fixture
def sample_user_data():
    return {
        "user_id": 123,
        "username": "testuser",
        "email": "test@example.com"
    }