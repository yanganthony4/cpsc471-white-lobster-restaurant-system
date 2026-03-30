# SQL Alchemy handles turning into correct SQL insert
from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base

# Python version of SQL table
class LoyaltyProgram(Base):
    __tablename__ = "LOYALTY_PROGRAM"

    Loyalty_id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(255), ForeignKey("CUSTOMER_ACCOUNT.email"), unique=True, nullable=False)
    pointsBalance = Column(Integer, nullable=False)