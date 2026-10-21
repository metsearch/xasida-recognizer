from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.schemas import XasidaCreate, XasidaOut
from src.database.database import get_db
from src.database.models import Xasida

router = APIRouter(prefix="/xasidas", tags=["xasidas"])


@router.get("", response_model=list[XasidaOut])
def list_xasidas(db: Session = Depends(get_db)):
    return db.query(Xasida).all()


@router.get("/{xasida_id}", response_model=XasidaOut)
def get_xasida(xasida_id: str, db: Session = Depends(get_db)):
    xasida = db.get(Xasida, xasida_id)
    if not xasida:
        raise HTTPException(status_code=404, detail="Xasida not found")
    return xasida


@router.post("", response_model=XasidaOut, status_code=201)
def create_xasida(body: XasidaCreate, db: Session = Depends(get_db)):
    xasida = Xasida(**body.model_dump())
    db.add(xasida)
    db.commit()
    db.refresh(xasida)
    return xasida


@router.delete("/{xasida_id}", status_code=204)
def delete_xasida(xasida_id: str, db: Session = Depends(get_db)):
    xasida = db.get(Xasida, xasida_id)
    if not xasida:
        raise HTTPException(status_code=404, detail="Xasida not found")
    db.delete(xasida)
    db.commit()
