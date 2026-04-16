from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class RestaurantTable(Base):
    __tablename__ = "RESTAURANT_TABLE"

    tableNumber = Column(Integer, primary_key=True, nullable=False)
    sectionName = Column(String(100), ForeignKey("SECTION.sectionName"), primary_key=True, nullable=False)
    availabilityStatus = Column(String(50), nullable=False, default="Available")
    capacity = Column(Integer, nullable=False)