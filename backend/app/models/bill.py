from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric

from app.database import Base


class Bill(Base):
    __tablename__ = "BILL"

    invoiceID = Column(Integer, primary_key=True, nullable=False)
    promoID = Column(Integer, ForeignKey("PROMOTION.promoID"), nullable=True)
    assignmentID = Column(Integer, ForeignKey("SEATING_ASSIGNMENT.assignmentID"), nullable=False, unique=True)
    totalAmount = Column(Numeric(10, 2), nullable=False, default=0.00)
    taxesAndFees = Column(Numeric(10, 2), nullable=False, default=0.00)
    isSettled = Column(Boolean, nullable=False, default=False)