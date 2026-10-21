import pytest

from src.database.models import AudioSegment, Version, Xasida
from src.services.indexer import index_version
from src.services.recognizer import recognize


@pytest.fixture
def xasida(db_session):
    x = Xasida(id="x-001", aka_name="Jeuzboul Mourid")
    db_session.add(x)
    db_session.commit()
    return x


@pytest.fixture
def version(db_session, xasida, audio_file):
    v = Version(id="v-001", xasida_id=xasida.id, audio_path=str(audio_file))
    db_session.add(v)
    db_session.commit()
    return v


class TestIndexVersion:
    def test_returns_positive_segment_count(self, qdrant, db_session, version):
        n = index_version(qdrant, db_session, version)
        assert n > 0

    def test_segments_stored_in_qdrant(self, qdrant, db_session, version):
        n = index_version(qdrant, db_session, version)
        from src.database.qdrant import COLLECTION
        info = qdrant.get_collection(COLLECTION)
        assert info.points_count == n

    def test_segments_stored_in_db(self, qdrant, db_session, version):
        n = index_version(qdrant, db_session, version)
        count = db_session.query(AudioSegment).filter_by(version_id=version.id).count()
        assert count == n

    def test_segment_payload_contains_xasida_id(self, qdrant, db_session, version):
        index_version(qdrant, db_session, version)
        from src.database.qdrant import COLLECTION
        results = qdrant.scroll(COLLECTION, limit=1)[0]
        assert results[0].payload["xasida_id"] == version.xasida_id


class TestRecognizer:
    def test_recognize_returns_correct_xasida(self, qdrant, db_session, version, monkeypatch, audio_file):
        monkeypatch.setattr("src.services.recognizer.get_client", lambda: qdrant)
        index_version(qdrant, db_session, version)
        result = recognize(str(audio_file))
        assert result["xasida_id"] == version.xasida_id

    def test_recognize_returns_high_confidence_on_same_audio(self, qdrant, db_session, version, monkeypatch, audio_file):
        monkeypatch.setattr("src.services.recognizer.get_client", lambda: qdrant)
        index_version(qdrant, db_session, version)
        result = recognize(str(audio_file))
        assert result["confidence"] > 0.5

    def test_recognize_empty_index_returns_null(self, qdrant, db_session, audio_file, monkeypatch):
        monkeypatch.setattr("src.services.recognizer.get_client", lambda: qdrant)
        result = recognize(str(audio_file))
        assert result["xasida_id"] is None
        assert result["confidence"] == 0.0
