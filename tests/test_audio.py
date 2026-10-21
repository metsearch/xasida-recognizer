import numpy as np
import pytest

from src.audio import SAMPLE_RATE, SEGMENT_DURATION, HOP_DURATION, VECTOR_SIZE, extract_embedding, segment_audio


def make_audio(seconds: float) -> np.ndarray:
    t = np.linspace(0, seconds, int(seconds * SAMPLE_RATE))
    return np.sin(2 * np.pi * 440 * t).astype(np.float32)


class TestSegmentAudio:
    def test_each_segment_has_correct_length(self):
        segments = segment_audio(make_audio(60))
        expected_len = int(SEGMENT_DURATION * SAMPLE_RATE)
        assert all(len(s) == expected_len for s in segments)

    def test_correct_number_of_segments(self):
        audio = make_audio(60)
        segments = segment_audio(audio)
        # floor((60 - SEGMENT_DURATION) / HOP_DURATION) + 1
        expected = int((60 - SEGMENT_DURATION) / HOP_DURATION) + 1
        assert len(segments) == expected

    def test_audio_shorter_than_segment_returns_empty(self):
        assert segment_audio(make_audio(5)) == []

    def test_audio_exactly_one_segment(self):
        assert len(segment_audio(make_audio(SEGMENT_DURATION))) == 1


class TestExtractEmbedding:
    def test_output_shape(self):
        embedding = extract_embedding(make_audio(SEGMENT_DURATION))
        assert embedding.shape == (VECTOR_SIZE,)

    def test_output_dtype(self):
        embedding = extract_embedding(make_audio(SEGMENT_DURATION))
        assert embedding.dtype == np.float32

    def test_output_is_finite(self):
        embedding = extract_embedding(make_audio(SEGMENT_DURATION))
        assert np.all(np.isfinite(embedding))

    def test_different_signals_produce_different_embeddings(self):
        e1 = extract_embedding(make_audio(SEGMENT_DURATION))
        e2 = extract_embedding(np.sin(2 * np.pi * 880 * np.linspace(0, SEGMENT_DURATION, int(SEGMENT_DURATION * SAMPLE_RATE))).astype(np.float32))
        assert not np.allclose(e1, e2)
