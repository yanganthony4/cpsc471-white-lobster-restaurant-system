# SQL Alchemy handles turning into correct SQL insert
from sqlalchemy import Column, Integer, String, Time, text, ForeignKey

from app.database import Base

class WaitlistEntry(Base):
    __tablename__ = "WAITLIST_ENTRY"

    waitlistID = Column(Integer, nullable=False, primary_key=True)
    email = Column(String(255), ForeignKey("CUSTOMER_ACCOUNT.email"), nullable=False,)
    specialRequests = Column(String(255))
    joinTime = Column(Time, nullable=False, server_default=text("CURRENT_TIME"))
    entryStatus = Column(String(50), nullable=False, default="Waiting")
    partySize = Column(Integer, nullable=False)
    estimatedWaitTime = Column(Integer, default=10)
