from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.fakultet import Fakultet
from ..schemas.fakultet import FakultetResponse

router = APIRouter(prefix="/fakulteti", tags=["Fakulteti"])

@router.get("/", response_model=List[FakultetResponse])
def get_all_fakulteti(db: Session = Depends(get_db)):
    fakulteti = db.query(Fakultet).order_by(Fakultet.naziv).all()
    return fakulteti
