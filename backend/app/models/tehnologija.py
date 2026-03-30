from sqlalchemy import Column, ForeignKey, Integer, String, Table

from ..database import Base

student_tehnologija = Table(
    "student_tehnologija",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("student.id", ondelete="CASCADE"), primary_key=True),
    Column("tehnologija_id", Integer, ForeignKey("tehnologija.id", ondelete="CASCADE"), primary_key=True),
)


class Tehnologija(Base):
    __tablename__ = "tehnologija"

    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(200), unique=True, nullable=False)
