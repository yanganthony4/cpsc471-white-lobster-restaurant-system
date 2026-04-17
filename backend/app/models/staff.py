from sqlalchemy import Column, Integer, String

from app.database import Base


class StaffUser(Base):
    __tablename__ = "STAFF_USER"

    employeeID   = Column(Integer,      primary_key=True, nullable=False, autoincrement=True)
    role         = Column(String(50),   nullable=False)
    name         = Column(String(100),  nullable=False)
    username     = Column(String(50),   nullable=False)
    passwordHash = Column(String(255),  nullable=False)