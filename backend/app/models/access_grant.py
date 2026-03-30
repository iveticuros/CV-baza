from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, func

from ..database import Base


class AccessGrant(Base):
    __tablename__ = "access_grant"

    id = Column(Integer, primary_key=True, index=True)
    company_profile_id = Column(Integer, ForeignKey("company_profile.id", ondelete="CASCADE"), nullable=False, index=True)
    max_cv_count = Column(Integer, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    used_cv_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    granted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
