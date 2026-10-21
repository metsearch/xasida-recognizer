import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.api.schemas import RecognizeOut
from src.audio import AUDIO_EXTENSIONS
from src.database.database import get_db
from src.database.models import Xasida
from src.services.recognizer import recognize

router = APIRouter(tags=["recognize"])


@router.post("/recognize", response_model=RecognizeOut)
async def recognize_xasida(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(audio.filename).suffix.lower()
    if suffix not in AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {suffix}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    result = recognize(tmp_path)
    Path(tmp_path).unlink(missing_ok=True)

    xasida = db.get(Xasida, result["xasida_id"]) if result["xasida_id"] else None

    return RecognizeOut(
        xasida_id=result["xasida_id"],
        aka_name=xasida.aka_name if xasida else None,
        author=xasida.author if xasida else None,
        confidence=result["confidence"],
        score=result["score"],
    )
