from sqlalchemy import Column, Integer, String
from ..database import Base

class Fakultet(Base):
    __tablename__ = "fakultet"

    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(50), nullable=False)
