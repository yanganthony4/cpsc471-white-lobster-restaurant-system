from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text

from app.database import Base


class SeatingAssignment(Base):
    __tablename__ = "SEATING_ASSIGNMENT"

    assignmentID = Column(Integer, primary_key=True, nullable=False)
    reservationID = Column(Integer, ForeignKey("RESERVATION.reservationID"), unique=True, nullable=True)
    waitlistID = Column(Integer, ForeignKey("WAITLIST_ENTRY.waitlistID"), unique=True, nullable=True)
    sectionName = Column(String(100), ForeignKey("SECTION.sectionName"), nullable=False)
    tableNumber = Column(Integer, nullable=False)
    employeeID = Column(Integer, ForeignKey("STAFF_USER.employeeID"), nullable=False)
    currentStatus = Column(String(50), nullable=False, default="Seated")
    startTime = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))