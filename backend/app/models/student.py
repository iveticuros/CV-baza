from sqlalchemy import Column, Integer, String
from ..database import Base

class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True)
    ime = Column(String(30), nullable=False)
    prezime = Column(String(30), nullable=False)
