import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sqlalchemy.orm import Session

from src.audio import AUDIO_EXTENSIONS, HOP_DURATION, SEGMENT_DURATION, extract_embedding, load_audio, segment_audio, stream_segments
from src.database.models import AudioSegment, Version
from src.database.qdrant import COLLECTION

EMBEDDING_MODEL = "mfcc"
EMBEDDING_VERSION = "1.0"


def index_version(client: QdrantClient, db: Session, version: Version) -> int:
    qdrant_points = []
    db_segments = []

    for i, seg in enumerate(stream_segments(version.audio_path)):
        seg_id = str(uuid.uuid4())
        start_time = round(i * HOP_DURATION, 2)
        end_time = round(start_time + SEGMENT_DURATION, 2)

        qdrant_points.append(PointStruct(
            id=seg_id,
            vector=extract_embedding(seg).tolist(),
            payload={
                "xasida_id": version.xasida_id,
                "reference_id": version.reference_id,
                "version_id": version.id,
                "segment_index": i,
                "start_time": start_time,
                "end_time": end_time,
            },
        ))

        db_segments.append(AudioSegment(
            id=seg_id,
            version_id=version.id,
            segment_index=i,
            start_time=start_time,
            end_time=end_time,
            embedding_model=EMBEDDING_MODEL,
            embedding_version=EMBEDDING_VERSION,
        ))

    client.upsert(collection_name=COLLECTION, points=qdrant_points)
    db.add_all(db_segments)
    db.commit()

    return len(qdrant_points)


def index_data_folder(data_dir: str = "./data") -> None:
    """Standalone script — indexes all audio files without DB."""
    from src.database.qdrant import ensure_collection, get_client

    client = get_client()
    ensure_collection(client)

    total = 0
    for khassida_dir in sorted(Path(data_dir).iterdir()):
        if not khassida_dir.is_dir():
            continue
        for audio_file in sorted(khassida_dir.glob("*")):
            if audio_file.suffix.lower() not in AUDIO_EXTENSIONS:
                continue
            audio = load_audio(str(audio_file))
            segments = segment_audio(audio)
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=extract_embedding(seg).tolist(),
                    payload={"khassida": khassida_dir.name, "segment": i, "source": str(audio_file)},
                )
                for i, seg in enumerate(segments)
            ]
            client.upsert(collection_name=COLLECTION, points=points)
            print(f"{audio_file.name} → {len(points)} segments")
            total += len(points)

    print(f"\nDone. {total} segments indexed.")
