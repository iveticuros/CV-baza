from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.tehnologija import Tehnologija
from ..schemas.student import TehnologijaResponse

router = APIRouter(prefix="/tehnologije", tags=["Tehnologije"])


@router.get("/", response_model=List[TehnologijaResponse])
def list_tehnologije(db: Session = Depends(get_db)):
    return db.query(Tehnologija).order_by(Tehnologija.naziv).all()
