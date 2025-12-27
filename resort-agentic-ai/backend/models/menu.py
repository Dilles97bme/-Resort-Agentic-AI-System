from sqlalchemy import Column, Integer, String, Float, Boolean
from backend.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)
