from sqlalchemy import Column, ForeignKey, Integer, Numeric

from app.database import Base


class BillItem(Base):
    __tablename__ = "BILL_ITEM"

    invoiceID = Column(Integer, ForeignKey("BILL.invoiceID"), primary_key=True, nullable=False)
    menuItemID = Column(Integer, ForeignKey("MENU_ITEM.menuItemID"), primary_key=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    priceAtOrder = Column(Numeric(10, 2), nullable=False)