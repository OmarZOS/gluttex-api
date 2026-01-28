# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import models
from server import app
from database.models import Base
import os

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_auth.db")

# Create engine and session factory
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency in FastAPI app
from dependencies import get_db

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Fixture to create database tables before tests and drop after
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

# Fixture for TestClient
@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

# Fixture for direct DB access
@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
