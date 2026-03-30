from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text

from ..database import Base


class Projekat(Base):
    __tablename__ = "projekti"

    id = Column(Integer, primary_key=True, index=True)
    datum_pocetka_izrade = Column(Date, nullable=False)
    datum_kraja_izrade_projekta = Column(Date, nullable=True)
    opis = Column(String(1000), nullable=False)
    id_studenta = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False, index=True)
