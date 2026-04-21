from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class LoyaltyProgram(Base):
    __tablename__ = "LOYALTY_PROGRAM"
    LoyaltyID = Column("Loyalty_id", Integer, primary_key=True, autoincrement=True, nullable=False)

    # email is the FK that lets the backend look up loyalty by customer email
    email = Column(String(255), ForeignKey("CUSTOMER_ACCOUNT.email"), unique=True, nullable=False)

    pointsBalance = Column(Integer, nullable=False, default=0)