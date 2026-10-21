from pathlib import Path

import librosa
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.api.schemas import VersionOut
from src.audio import AUDIO_EXTENSIONS
from src.database.database import get_db
from src.database.models import Version, Xasida

router = APIRouter(tags=["versions"])


@router.get("/xasidas/{xasida_id}/versions", response_model=list[VersionOut])
def list_versions(xasida_id: str, db: Session = Depends(get_db)):
    xasida = db.get(Xasida, xasida_id)
    if not xasida:
        raise HTTPException(status_code=404, detail="Xasida not found")
    return db.query(Version).filter(Version.xasida_id == xasida_id).all()


@router.post("/xasidas/{xasida_id}/versions", response_model=VersionOut, status_code=201)
async def create_version(
    xasida_id: str,
    audio: UploadFile = File(...),
    reference_id: str | None = Form(None),
    artist: str | None = Form(None),
    year: int | None = Form(None),
    source: str | None = Form(None),
    recording_quality: str | None = Form(None),
    db: Session = Depends(get_db),
):
    xasida = db.get(Xasida, xasida_id)
    if not xasida:
        raise HTTPException(status_code=404, detail="Xasida not found")

    suffix = Path(audio.filename).suffix.lower()
    if suffix not in AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {suffix}")

    dest_dir = Path("data") / xasida.aka_name.lower().replace(" ", "_")
    dest_dir.mkdir(parents=True, exist_ok=True)
    audio_path = dest_dir / audio.filename

    content = await audio.read()
    audio_path.write_bytes(content)

    duration_seconds = librosa.get_duration(path=str(audio_path))

    version = Version(
        xasida_id=xasida_id,
        reference_id=reference_id,
        artist=artist,
        year=year,
        audio_path=str(audio_path),
        duration=round(duration_seconds, 2),
        source=source,
        recording_quality=recording_quality,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.delete("/versions/{version_id}", status_code=204)
def delete_version(version_id: str, db: Session = Depends(get_db)):
    version = db.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    db.delete(version)
    db.commit()
