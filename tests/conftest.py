"""
Shared pytest configuration for all tests
"""

import sys
from pathlib import Path

# Add project root to Python path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402
from src.database import Base, engine  # noqa: E402


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
