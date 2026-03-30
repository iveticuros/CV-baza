from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from ..database import Base


class DeletionRequest(Base):
    __tablename__ = "deletion_request"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note = Column(String(500), nullable=True)
