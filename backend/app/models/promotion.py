from sqlalchemy import Column, Date, Integer, Numeric, String

from app.database import Base


class Promotion(Base):
    __tablename__ = "PROMOTION"

    promoID = Column(Integer, primary_key=True, nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    discountAmount = Column(Numeric(10, 2), nullable=False)
    eligibilityRules = Column(String(255), nullable=True)