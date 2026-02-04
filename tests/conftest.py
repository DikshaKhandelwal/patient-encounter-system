"""
Shared pytest fixtures for all test files
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import Base, engine


@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test function"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create TestClient instance with fresh database"""
    return TestClient(app)
