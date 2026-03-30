from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ProjekatIn(BaseModel):
    datum_pocetka_izrade: date
    datum_kraja_izrade_projekta: Optional[date] = None
    opis: str = Field(..., max_length=1000)


class StudentRegisterRequest(BaseModel):
    name: str = Field(..., max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    consent_data_processing: bool
    ime: str = Field(..., max_length=100)
    prezime: str = Field(..., max_length=100)
    kontakt_telefon: Optional[str] = Field(None, max_length=30)
    datum_rodjenja: Optional[date] = None
    adresa: Optional[str] = Field(None, max_length=500)
    prosek: Optional[float] = Field(None, ge=0, le=10)
    fakultet_id: int
    projekti: List[ProjekatIn] = Field(default_factory=list)
    tehnologija_ids: List[int] = Field(default_factory=list)

    @field_validator("consent_data_processing")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Morate prihvatiti obradu podataka u skladu sa ZZPL.")
        return v
