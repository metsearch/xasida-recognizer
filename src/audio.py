from collections.abc import Iterator

import librosa
import numpy as np
import soundfile as sf

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

SAMPLE_RATE = 22050
SEGMENT_DURATION = 15  # seconds
HOP_DURATION = 7  # overlap: segment every 7s → ~50% overlap

# MFCC(40)*2 + Chroma(12)*2 + SpectralContrast(7)*2 = 118
VECTOR_SIZE = 118


def stream_segments(path: str) -> Iterator[np.ndarray]:
    """Yield 15-second segments without loading the full file into memory."""
    with sf.SoundFile(path) as f:
        native_sr = f.samplerate
        segment_frames = int(SEGMENT_DURATION * native_sr)
        hop_frames = int(HOP_DURATION * native_sr)
        total_frames = len(f)

        for start in range(0, total_frames - segment_frames + 1, hop_frames):
            f.seek(start)
            chunk = f.read(frames=segment_frames, dtype="float32", always_2d=False)

            if chunk.ndim > 1:
                chunk = chunk.mean(axis=1)

            if native_sr != SAMPLE_RATE:
                chunk = librosa.resample(chunk, orig_sr=native_sr, target_sr=SAMPLE_RATE)

            yield chunk


def load_audio(path: str) -> np.ndarray:
    """Load full audio into memory — use only for short files (tests)."""
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    return audio


def segment_audio(audio: np.ndarray) -> list[np.ndarray]:
    """Segment an in-memory array — use only for short audio (tests)."""
    segment_len = int(SEGMENT_DURATION * SAMPLE_RATE)
    hop_len = int(HOP_DURATION * SAMPLE_RATE)
    segments = []
    for start in range(0, len(audio) - segment_len + 1, hop_len):
        segments.append(audio[start : start + segment_len])
    return segments


def extract_embedding(segment: np.ndarray) -> np.ndarray:
    mfcc = librosa.feature.mfcc(y=segment, sr=SAMPLE_RATE, n_mfcc=40)
    chroma = librosa.feature.chroma_stft(y=segment, sr=SAMPLE_RATE)
    contrast = librosa.feature.spectral_contrast(y=segment, sr=SAMPLE_RATE)

    features = np.concatenate([
        mfcc.mean(axis=1), mfcc.std(axis=1),
        chroma.mean(axis=1), chroma.std(axis=1),
        contrast.mean(axis=1), contrast.std(axis=1),
    ])
    return features.astype(np.float32)
