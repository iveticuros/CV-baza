from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String

from ..database import Base


class StudijskiProgram(Base):
    __tablename__ = "studijski_program"

    id = Column(Integer, primary_key=True, index=True)
    fakultet_id = Column(Integer, ForeignKey("fakultet.id"), nullable=False, index=True)
    tip_studija = Column(String(40), nullable=False)
    godina = Column(Integer, nullable=False)
    datum_pocetka = Column(Date, nullable=False)
    datum_kraja = Column(Date, nullable=True)
