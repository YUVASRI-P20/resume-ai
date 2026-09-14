import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON, Boolean, Uuid
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.user import User

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    notification_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship(User, backref="notifications")

class RecruiterReport(Base):
    __tablename__ = "recruiter_reports"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recruiter_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_data = Column(JSON, nullable=False)
    format_type = Column(String(20), default="JSON")
    created_at = Column(DateTime, default=datetime.utcnow)
    recruiter = relationship(User, foreign_keys=[recruiter_id], backref="generated_reports")
    candidate = relationship(User, foreign_keys=[candidate_id], backref="recruiter_reports")
