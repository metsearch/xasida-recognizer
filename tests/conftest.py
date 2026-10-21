import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.audio import SAMPLE_RATE
from src.database.database import get_db
from src.database.models import Base
from src.database.qdrant import COLLECTION, ensure_collection


@pytest.fixture
def db_session():
    # StaticPool: all connections reuse the same in-memory DB
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def qdrant():
    client = QdrantClient(":memory:")
    ensure_collection(client)
    return client


@pytest.fixture
def api_client(db_session, qdrant, monkeypatch):
    monkeypatch.setattr("main.get_client", lambda: qdrant)
    monkeypatch.setattr("src.api.index.get_client", lambda: qdrant)
    monkeypatch.setattr("src.services.recognizer.get_client", lambda: qdrant)

    from main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def audio_file(tmp_path):
    """15-second sine wave saved as WAV."""
    duration = 15.0
    t = np.linspace(0, duration, int(duration * SAMPLE_RATE))
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    path = tmp_path / "test.wav"
    sf.write(str(path), audio, SAMPLE_RATE)
    return path
