from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func

from ..database import Base


class CompanyStudentAccess(Base):
    __tablename__ = "company_student_access"

    id = Column(Integer, primary_key=True, index=True)
    access_grant_id = Column(Integer, ForeignKey("access_grant.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (UniqueConstraint("access_grant_id", "student_id", name="uq_grant_student"),)
