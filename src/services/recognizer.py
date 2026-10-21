from collections import Counter

from src.audio import extract_embedding, stream_segments
from src.database.qdrant import COLLECTION, get_client


def recognize(audio_path: str, top_k: int = 5) -> dict:
    client = get_client()
    votes: Counter = Counter()
    best: dict[str, dict] = {}

    for seg in stream_segments(audio_path):
        response = client.query_points(
            collection_name=COLLECTION,
            query=extract_embedding(seg).tolist(),
            limit=top_k,
        )
        for hit in response.points:
            xasida_id = hit.payload["xasida_id"]
            votes[xasida_id] += 1
            if xasida_id not in best or hit.score > best[xasida_id]["score"]:
                best[xasida_id] = {
                    "score": hit.score,
                    "version_id": hit.payload.get("version_id"),
                    "start_time": hit.payload.get("start_time"),
                }

    if not votes:
        return {"xasida_id": None, "confidence": 0.0, "score": 0.0, "version_id": None, "start_time": None}

    winner_id, vote_count = votes.most_common(1)[0]
    confidence = vote_count / sum(votes.values())

    return {
        "xasida_id": winner_id,
        "version_id": best[winner_id]["version_id"],
        "start_time": best[winner_id]["start_time"],
        "confidence": round(confidence, 3),
        "score": round(best[winner_id]["score"], 3),
    }
