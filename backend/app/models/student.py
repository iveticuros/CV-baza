from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func

from ..database import Base
from ..types.encrypted import EncryptedString


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    ime = Column(String(100), nullable=False)
    prezime = Column(String(100), nullable=False)
    kontakt_telefon = Column(EncryptedString(512), nullable=True)
    datum_rodjenja_enc = Column("datum_rodjenja", EncryptedString(512), nullable=True)
    adresa = Column(EncryptedString(1024), nullable=True)
    prosek = Column(Float, nullable=True)
    fakultet_id = Column(Integer, ForeignKey("fakultet.id"), nullable=False, index=True)
    cv_file_path = Column(String(500), nullable=True)
    cv_original_filename = Column(String(255), nullable=True)
    last_edit_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)
