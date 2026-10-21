from pydantic import BaseModel


# ── Xasida ────────────────────────────────────────────────────────────────────

class XasidaCreate(BaseModel):
    og_name: str | None = None
    aka_name: str
    author: str = "Cheikh Ahmadou Bamba"
    language: str = "ar"
    pdf_path: str | None = None
    ar_pdf_path: str | None = None
    fr_pdf_path: str | None = None
    an_pdf_path: str | None = None
    description: str | None = None


class XasidaOut(XasidaCreate):
    id: str
    model_config = {"from_attributes": True}


# ── Reference ─────────────────────────────────────────────────────────────────

class ReferenceCreate(BaseModel):
    name: str
    year: int | None = None
    url: str | None = None


class ReferenceOut(ReferenceCreate):
    id: str
    model_config = {"from_attributes": True}


# ── Version ───────────────────────────────────────────────────────────────────

class VersionCreate(BaseModel):
    reference_id: str | None = None
    artist: str | None = None
    year: int | None = None
    source: str | None = None
    recording_quality: str | None = None


class VersionOut(BaseModel):
    id: str
    xasida_id: str
    reference_id: str | None = None
    artist: str | None = None
    year: int | None = None
    audio_path: str
    duration: float | None = None
    source: str | None = None
    recording_quality: str | None = None
    model_config = {"from_attributes": True}


# ── Index ─────────────────────────────────────────────────────────────────────

class IndexOut(BaseModel):
    version_id: str
    segments_indexed: int


# ── Recognize ─────────────────────────────────────────────────────────────────

class RecognizeOut(BaseModel):
    xasida_id: str | None
    aka_name: str | None
    author: str | None
    confidence: float
    score: float
