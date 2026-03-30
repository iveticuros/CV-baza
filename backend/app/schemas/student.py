from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjekatOut(BaseModel):
    id: int
    datum_pocetka_izrade: date
    datum_kraja_izrade_projekta: Optional[date] = None
    opis: str

    class Config:
        from_attributes = True


class TehnologijaOut(BaseModel):
    id: int
    naziv: str

    class Config:
        from_attributes = True


class StudentProfileOut(BaseModel):
    id: int
    ime: str
    prezime: str
    kontakt_telefon: Optional[str] = None
    datum_rodjenja: Optional[date] = None
    adresa: Optional[str] = None
    prosek: Optional[float] = None
    fakultet_id: int
    faculty_name: Optional[str] = None
    has_cv: bool
    last_edit_at: Optional[datetime] = None
    can_edit_until: Optional[datetime] = None
    projekti: List[ProjekatOut] = []
    tehnologije: List[TehnologijaOut] = []


class ProjekatUpdate(BaseModel):
    id: Optional[int] = None
    datum_pocetka_izrade: date
    datum_kraja_izrade_projekta: Optional[date] = None
    opis: str = Field(..., max_length=1000)


class StudentProfileUpdate(BaseModel):
    ime: Optional[str] = Field(None, max_length=100)
    prezime: Optional[str] = Field(None, max_length=100)
    kontakt_telefon: Optional[str] = Field(None, max_length=30)
    datum_rodjenja: Optional[date] = None
    adresa: Optional[str] = Field(None, max_length=500)
    prosek: Optional[float] = Field(None, ge=0, le=10)
    fakultet_id: Optional[int] = None
    projekti: Optional[List[ProjekatUpdate]] = None
    tehnologija_ids: Optional[List[int]] = None


class StudentPublicCompany(BaseModel):
    id: int
    ime: str
    prezime: str
    prosek: Optional[float] = None
    fakultet_id: int
    faculty_name: Optional[str] = None
    tehnologije: List[str] = []


class PaginatedStudents(BaseModel):
    items: List[StudentPublicCompany]
    total: int
    page: int
    page_size: int


class TehnologijaResponse(BaseModel):
    id: int
    naziv: str

    class Config:
        from_attributes = True
