from sqlalchemy import Column, Integer, Numeric, String

from app.database import Base


class MenuItem(Base):
    __tablename__ = "MENU_ITEM"

    menuItemID = Column(Integer, primary_key=True, nullable=False)
    description = Column(String(255), nullable=True)
    currentPrice = Column(Numeric(10, 2), nullable=False)
    name = Column(String(100), nullable=False)