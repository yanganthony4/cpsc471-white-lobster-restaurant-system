from sqlalchemy import Column, String

from app.database import Base


class CustomerAccount(Base):
    __tablename__ = "CUSTOMER_ACCOUNT"

    email        = Column(String(255), primary_key=True, nullable=False)
    phoneNumber  = Column(String(50))
    name         = Column(String(100), nullable=False)
    username     = Column(String(50),  nullable=False)
    passwordHash = Column(String(255), nullable=False) # passwordHash instead