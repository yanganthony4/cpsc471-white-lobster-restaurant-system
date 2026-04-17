from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class Reservation(Base):
    __tablename__ = "RESERVATION"

    reservationID = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    email         = Column(String(255), ForeignKey("CUSTOMER_ACCOUNT.email"), nullable=False)

    specialRequests     = Column(String(255))
    partySize           = Column(Integer, nullable=False)
    # single reservationDateTime DATETIME column in db schema
    reservationDateTime = Column(DateTime, nullable=False)