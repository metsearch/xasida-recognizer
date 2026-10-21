from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import ReferenceCreate, ReferenceOut
from src.database.database import get_db
from src.database.models import Reference

router = APIRouter(prefix="/references", tags=["references"])


@router.get("", response_model=list[ReferenceOut])
def list_references(db: Session = Depends(get_db)):
    return db.query(Reference).all()


@router.get("/{reference_id}", response_model=ReferenceOut)
def get_reference(reference_id: str, db: Session = Depends(get_db)):
    ref = db.get(Reference, reference_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    return ref


@router.post("", response_model=ReferenceOut, status_code=201)
def create_reference(body: ReferenceCreate, db: Session = Depends(get_db)):
    ref = Reference(**body.model_dump())
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref


@router.delete("/{reference_id}", status_code=204)
def delete_reference(reference_id: str, db: Session = Depends(get_db)):
    ref = db.get(Reference, reference_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    db.delete(ref)
    db.commit()
