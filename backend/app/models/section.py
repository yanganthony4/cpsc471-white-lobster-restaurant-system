from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class Section(Base):
    __tablename__ = "SECTION"

    sectionName = Column(String(100), primary_key=True, nullable=False)
    employeeID = Column(Integer, ForeignKey("STAFF_USER.employeeID"), nullable=True)