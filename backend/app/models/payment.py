from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, text

from app.database import Base


class Payment(Base):
    __tablename__ = "PAYMENT"

    paymentID = Column(Integer, primary_key=True, nullable=False)
    invoiceID = Column(Integer, ForeignKey("BILL.invoiceID"), nullable=False)
    paymentMethod = Column(String(50), nullable=False)
    timeStamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    amount = Column(Numeric(10, 2), nullable=False)