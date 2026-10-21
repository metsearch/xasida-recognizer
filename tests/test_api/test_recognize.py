import io


def test_recognize_unsupported_format(api_client):
    r = api_client.post(
        "/recognize",
        files={"audio": ("clip.txt", io.BytesIO(b"not audio"), "text/plain")},
    )
    assert r.status_code == 400
    assert "Unsupported format" in r.json()["detail"]


def test_recognize_returns_null_when_index_empty(api_client, audio_file):
    with open(audio_file, "rb") as f:
        r = api_client.post(
            "/recognize",
            files={"audio": ("clip.wav", f, "audio/wav")},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["xasida_id"] is None
    assert data["confidence"] == 0.0
