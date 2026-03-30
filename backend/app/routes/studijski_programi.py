from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.fakultet import Fakultet
from ..models.studijski_program import StudijskiProgram
from ..schemas.studijski_program import StudijskiProgramResponse

router = APIRouter(prefix="/studijski-programi", tags=["Studijski programi"])


@router.get("/", response_model=List[StudijskiProgramResponse])
def list_programs(
    db: Session = Depends(get_db),
    fakultet_id: Optional[int] = Query(None),
):
    q = db.query(StudijskiProgram)
    if fakultet_id is not None:
        q = q.filter(StudijskiProgram.fakultet_id == fakultet_id)
    rows = q.order_by(StudijskiProgram.id).all()
    out: list[StudijskiProgramResponse] = []
    for r in rows:
        fac = db.query(Fakultet).filter(Fakultet.id == r.fakultet_id).first()
        out.append(
            StudijskiProgramResponse(
                id=r.id,
                fakultet_id=r.fakultet_id,
                tip_studija=r.tip_studija,
                godina=r.godina,
                datum_pocetka=r.datum_pocetka,
                datum_kraja=r.datum_kraja,
                fakultet_naziv=fac.naziv if fac else None,
            )
        )
    return out
