import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Load environment variables from .env file
load_dotenv()

IS_TESTING = os.getenv("PYTEST_CURRENT_TEST") is not None or "pytest" in sys.modules

if IS_TESTING:
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

# Fall back to test database if DATABASE_URL not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///test.db"

# Database Setup
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL in ("sqlite:///:memory:", "sqlite:///test.db"):
        engine_kwargs["poolclass"] = StaticPool
else:
    engine_kwargs.update(
        {
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_size": 5,  # Connection pool size
            "max_overflow": 10,  # Max overflow connections
        }
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
