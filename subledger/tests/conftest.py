import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_session_local():
        return TestSession()

    import app.main as main_module

    original_session_local = main_module.SessionLocal
    main_module.SessionLocal = TestSession

    with TestClient(app) as test_client:
        yield test_client

    main_module.SessionLocal = original_session_local
