from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import IndexOut
from src.database.database import get_db
from src.database.models import Version
from src.database.qdrant import ensure_collection, get_client
from src.services.indexer import index_version

router = APIRouter(prefix="/index", tags=["index"])


@router.post("/{version_id}", response_model=IndexOut)
def index_one_version(version_id: str, db: Session = Depends(get_db)):
    version = db.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    client = get_client()
    ensure_collection(client)
    n = index_version(client, db, version)
    return IndexOut(version_id=version_id, segments_indexed=n)


@router.post("/all", response_model=list[IndexOut])
def index_all_versions(db: Session = Depends(get_db)):
    versions = db.query(Version).all()
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found in database")

    client = get_client()
    ensure_collection(client)

    results = []
    for version in versions:
        n = index_version(client, db, version)
        results.append(IndexOut(version_id=version.id, segments_indexed=n))

    return results
