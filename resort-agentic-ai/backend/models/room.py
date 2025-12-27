from sqlalchemy import Column, Integer, Boolean
from backend.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer, unique=True, index=True)
    is_available = Column(Boolean, default=True)
