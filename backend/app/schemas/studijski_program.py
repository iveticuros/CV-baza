from datetime import date
from typing import Optional

from pydantic import BaseModel


class StudijskiProgramResponse(BaseModel):
    id: int
    fakultet_id: int
    tip_studija: str
    godina: int
    datum_pocetka: date
    datum_kraja: Optional[date] = None
    fakultet_naziv: Optional[str] = None

    class Config:
        from_attributes = True
