from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer)
    items = Column(String)
    quantity = Column(String)
    total_amount = Column(Float)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
