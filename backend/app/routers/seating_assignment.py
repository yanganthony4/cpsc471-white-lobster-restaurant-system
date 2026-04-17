from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.seating_assignment import SeatingAssignment
from app.models.restaurant_table import RestaurantTable
from app.models.reservation import Reservation
from app.models.waitlistentry import WaitlistEntry
from app.schemas.seating_assignment import (
    SeatingAssignmentCreate, SeatingAssignmentUpdate, SeatingAssignmentResponse,
)

router = APIRouter()
VALID_ASSIGNMENT_STATUSES = {"Seated", "Completed", "Cancelled"}


# GET /seating-assignments/
@router.get("/", response_model=List[SeatingAssignmentResponse])
def list_seating_assignments(db: Session = Depends(get_db)):
    return db.query(SeatingAssignment).order_by(SeatingAssignment.assignmentID).all()


# POST /seating-assignments/  — transactional: also marks table occupied + source entry seated
@router.post("/", response_model=SeatingAssignmentResponse)
def create_seating_assignment(assignment: SeatingAssignmentCreate, db: Session = Depends(get_db)):
    if assignment.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(400, detail="Invalid seating assignment status")

    # XOR constraint
    if (assignment.reservationID is None) == (assignment.waitlistID is None):
        raise HTTPException(400, detail="Exactly one of reservationID or waitlistID must be provided")

    # Check not already assigned
    if assignment.reservationID is not None:
        if db.query(SeatingAssignment).filter(
            SeatingAssignment.reservationID == assignment.reservationID
        ).first():
            raise HTTPException(400, detail="This reservation already has a seating assignment")

    if assignment.waitlistID is not None:
        if db.query(SeatingAssignment).filter(
            SeatingAssignment.waitlistID == assignment.waitlistID
        ).first():
            raise HTTPException(400, detail="This waitlist entry already has a seating assignment")

    # Create assignment
    new_assignment = SeatingAssignment(
        reservationID=assignment.reservationID,
        waitlistID=assignment.waitlistID,
        sectionName=assignment.sectionName,
        tableNumber=assignment.tableNumber,
        employeeID=assignment.employeeID,
        currentStatus=assignment.currentStatus,
    )
    db.add(new_assignment)

    # TRANSACTION: mark table as Occupied
    table = db.query(RestaurantTable).filter(
        RestaurantTable.tableNumber == assignment.tableNumber,
        RestaurantTable.sectionName == assignment.sectionName,
    ).first()
    if table:
        table.availabilityStatus = "Occupied"

    # TRANSACTION: mark source entry as Seated
    if assignment.reservationID is not None:
        # Reservations don't have a status field in the current schema — nothing to update
        pass
    if assignment.waitlistID is not None:
        wl = db.query(WaitlistEntry).filter(
            WaitlistEntry.waitlistID == assignment.waitlistID
        ).first()
        if wl:
            wl.entryStatus = "Seated"

    db.commit()
    db.refresh(new_assignment)
    return new_assignment


# GET /seating-assignments/{assignment_id}
@router.get("/{assignment_id}", response_model=SeatingAssignmentResponse)
def get_seating_assignment(assignment_id: int, db: Session = Depends(get_db)):
    obj = db.query(SeatingAssignment).filter(
        SeatingAssignment.assignmentID == assignment_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Seating assignment not found")
    return obj


# PUT /seating-assignments/{assignment_id}  — transactional: free table when Completed/Cancelled
@router.put("/{assignment_id}", response_model=SeatingAssignmentResponse)
def update_seating_assignment(
    assignment_id: int, update: SeatingAssignmentUpdate, db: Session = Depends(get_db)
):
    if update.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(400, detail="Invalid seating assignment status")

    obj = db.query(SeatingAssignment).filter(
        SeatingAssignment.assignmentID == assignment_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Seating assignment not found")

    old_status = obj.currentStatus
    obj.currentStatus = update.currentStatus

    # Free the table when the party leaves or assignment is cancelled
    if update.currentStatus in ("Completed", "Cancelled") and old_status == "Seated":
        table = db.query(RestaurantTable).filter(
            RestaurantTable.tableNumber == obj.tableNumber,
            RestaurantTable.sectionName == obj.sectionName,
        ).first()
        if table:
            table.availabilityStatus = "Available"

    db.commit(); db.refresh(obj)
    return obj


# DELETE /seating-assignments/{assignment_id}
@router.delete("/{assignment_id}")
def delete_seating_assignment(assignment_id: int, db: Session = Depends(get_db)):
    obj = db.query(SeatingAssignment).filter(
        SeatingAssignment.assignmentID == assignment_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Seating assignment not found")
    db.delete(obj); db.commit()
    return {"message": "Seating assignment successfully deleted"}