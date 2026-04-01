from datetime import datetime
from pydantic import BaseModel


class SeatingAssignmentCreate(BaseModel):
    reservationID: int | None = None
    waitlistID: int | None = None
    sectionName: str
    tableNumber: int
    employeeID: int
    currentStatus: str = "Seated"


class SeatingAssignmentUpdate(BaseModel):
    currentStatus: str


class SeatingAssignmentResponse(BaseModel):
    assignmentID: int
    reservationID: int | None = None
    waitlistID: int | None = None
    sectionName: str
    tableNumber: int
    employeeID: int
    currentStatus: str
    startTime: datetime

    model_config = {"from_attributes": True}