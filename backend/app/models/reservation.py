# SQL Alchemy handles turning into correct SQL insert
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base

class Reservation(Base):
    __tablename__ = "RESERVATION"

    reservationID = Column(Integer, nullable=False, primary_key=True)
    email = Column(String(255), ForeignKey("CUSTOMER_ACCOUNT.email"), nullable=False)
    specialRequests = Column(String(255))
    partySize = Column(Integer, nullable=False)
    reservationDateTime = Column(DateTime, nullable=False)
