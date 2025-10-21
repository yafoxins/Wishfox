from __future__ import annotations

import os
from collections.abc import Generator

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from pathlib import Path

# Ensure env variables are set before importing application modules
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("CSRF_SECRET", "test-csrf")
os.environ.setdefault("BOT_TOKEN", "123456:TEST")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("TELEGRAM_BOT_NAME", "wishlist_bot_test")

from app.config import settings  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.utils import redis as redis_utils  # noqa: E402
from app.worker import send_notification  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[TestClient, None, None]:
    fake_redis = fakeredis.FakeRedis()

    def _fake_get_redis():
        return fake_redis

    monkeypatch.setattr(redis_utils, "get_redis", _fake_get_redis)
    monkeypatch.setattr(send_notification, "delay", lambda *args, **kwargs: None)
    media_dir = tmp_path / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "media_root", str(media_dir))
    with TestClient(app) as test_client:
        yield test_client
