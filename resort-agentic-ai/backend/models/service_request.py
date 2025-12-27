from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base
from datetime import datetime


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer)
    request_type = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
