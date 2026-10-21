# xasida-recognizer

A Shazam-like audio recognition system for xasidas — devotional poems composed by Cheikh Ahmadou Bamba Mbacké, founder of the Mouride brotherhood.

Given an audio snippet (a recording, a voice memo, a live recitation), the system identifies which xasida is being recited, regardless of the version, artist, or recording quality.

---

## How it works

1. Audio files (multiple versions of each xasida) are split into overlapping 15-second segments
2. Each segment is encoded into a vector embedding using an audio feature extractor
3. Embeddings are indexed in Qdrant alongside metadata pointing back to the xasida, reference, and version
4. At query time, a short audio clip is encoded and matched against the index via nearest-neighbor search
5. A majority vote across matched segments returns the recognized xasida with a confidence score

---

## Architecture

```
┌─────────────────────────────────┐     ┌──────────────────────────────┐
│         PostgreSQL / SQLite      │     │           Qdrant              │
│                                 │     │                              │
│  xasidas        references      │     │  collection: xasida_segments │
│  versions       audio_segments  │◄────│  payload: xasida_id,         │
│                                 │     │           version_id,         │
│                                 │     │           start_time, ...     │
└─────────────────────────────────┘     └──────────────────────────────┘
```

The SQL database holds all structured metadata. Qdrant holds vectors and only the IDs needed to join back to the SQL database.

---

## Database schema

### `xasidas`
The canonical xasida entity.

| Column | Type | Description |
|---|---|---|
| `id` | str | Unique identifier (e.g. `x_001`) |
| `og_name` | str | Original name (Arabic script) |
| `aka_name` | str | Commonly used name (e.g. `Jeuzboul Mourid`) |
| `author` | str | Default: `Cheikh Ahmadou Bamba` |
| `language` | str | Default: `ar` |
| `pdf_path` | str | Original PDF |
| `ar_pdf_path` | str | Arabic PDF |
| `fr_pdf_path` | str | French translation PDF |
| `an_pdf_path` | str | Annotated PDF |
| `description` | str | Short description |

### `references`
A published edition or collection in which a xasida appears (diwan, book, cassette series, etc.).

| Column | Type | Description |
|---|---|---|
| `id` | str | Unique identifier (e.g. `ref_001`) |
| `name` | str | Name of the reference |
| `year` | int | Publication or release year |
| `url` | str | Link to source if available |

### `versions`
A specific audio recording of a xasida, linked to a reference.

| Column | Type | Description |
|---|---|---|
| `id` | str | Unique identifier (e.g. `ver_001`) |
| `xasida_id` | str | FK → `xasidas.id` |
| `reference_id` | str | FK → `references.id` |
| `artist` | str | Who recites it |
| `year` | int | Recording year |
| `audio_path` | str | Path to audio file |
| `duration` | float | Duration in seconds |
| `source` | str | Origin of the recording |
| `recording_quality` | str | e.g. `high`, `medium`, `low` |

### `audio_segments`
Registry of all indexed segments. The actual vector lives in Qdrant.

| Column | Type | Description |
|---|---|---|
| `id` | str | Unique identifier, matches Qdrant point ID |
| `version_id` | str | FK → `versions.id` |
| `segment_index` | int | Position of the segment within the version |
| `start_time` | float | Start time in seconds |
| `end_time` | float | End time in seconds |
| `embedding_model` | str | Model used to compute the embedding |
| `embedding_version` | str | Version of the model |

### Qdrant — `xasida_segments`

```json
{
  "id": "segment_000123",
  "vector": [0.12, -0.04, "..."],
  "payload": {
    "xasida_id": "x_001",
    "reference_id": "ref_002",
    "version_id": "ver_005",
    "segment_index": 14,
    "start_time": 340.0,
    "end_time": 355.0
  }
}
```

---

## Project structure

```
xasida-recognizer/
├── data/
│   ├── jeuzbou/          # audio files for Jeuzboul Mourid
│   └── mawahibou/        # audio files for Mawahiboul Mourid
├── src/
│   ├── audio.py          # audio loading, segmentation, embedding extraction
│   ├── indexer.py        # index audio files into Qdrant
│   └── recognizer.py     # recognition logic (nearest-neighbor + majority vote)
├── main.py               # FastAPI API
├── docker-compose.yml    # Qdrant service
├── .env.example
└── pyproject.toml
```

---

## Getting started

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker

```bash
# 1. Clone and install dependencies
git clone <repo>
cd xasida-recognizer
uv sync

# 2. Configure environment
cp .env.example .env

# 3. Start Qdrant
docker compose up -d

# 4. Place audio files
#    data/jeuzbou/jeuzbou.mp3
#    data/mawahibou/mawahibou.mp3

# 5. Index xasidas
uv run python -c "from src.indexer import index_data_folder; index_data_folder()"

# 6. Start the API
uv run python main.py
```

**Recognize a xasida:**

```bash
curl -X POST http://localhost:8000/recognize \
  -F "audio=@clip.mp3"
```

```json
{
  "khassida": "jeuzbou",
  "confidence": 0.87,
  "score": 0.94
}
```

---

## Roadmap

- [ ] SQL database integration (xasidas, references, versions, audio_segments)
- [ ] Neural embeddings with CLAP for cross-version robustness
- [ ] Multi-version support per xasida
- [ ] Return timestamp position within the xasida
- [ ] Web interface
