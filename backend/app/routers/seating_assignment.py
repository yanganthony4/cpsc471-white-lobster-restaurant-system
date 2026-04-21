from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.seating_assignment import SeatingAssignment
from app.models.restaurant_table import RestaurantTable
from app.models.reservation import Reservation
from app.models.waitlistentry import WaitlistEntry
from app.schemas.seating_assignment import (
    SeatingAssignmentCreate,
    SeatingAssignmentUpdate,
    SeatingAssignmentResponse,
)

router = APIRouter()

VALID_ASSIGNMENT_STATUSES = {"Seated", "Completed", "Cancelled"}


# GET /seating-assignments/
@router.get("/", response_model=List[SeatingAssignmentResponse])
def list_seating_assignments(db: Session = Depends(get_db)):
    return db.query(SeatingAssignment).order_by(SeatingAssignment.assignmentID).all()


# POST /seating-assignments/
@router.post("/", response_model=SeatingAssignmentResponse)
def create_seating_assignment(
    assignment: SeatingAssignmentCreate,
    db: Session = Depends(get_db),
):
    # Validate status 
    if assignment.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status '{assignment.currentStatus}'. "
                f"Allowed values: {sorted(VALID_ASSIGNMENT_STATUSES)}"
            ),
        )

    # XOR constraint
    has_reservation = assignment.reservationID is not None
    has_waitlist    = assignment.waitlistID    is not None

    if has_reservation and has_waitlist:
        raise HTTPException(
            status_code=400,
            detail="Provide reservationID OR waitlistID — not both.",
        )
    if not has_reservation and not has_waitlist:
        raise HTTPException(
            status_code=400,
            detail="Exactly one of reservationID or waitlistID must be provided.",
        )

    # Duplicate-assignment guard 
    if has_reservation:
        if db.query(SeatingAssignment).filter(
            SeatingAssignment.reservationID == assignment.reservationID
        ).first():
            raise HTTPException(
                status_code=400,
                detail=f"Reservation {assignment.reservationID} already has a seating assignment.",
            )

    if has_waitlist:
        if db.query(SeatingAssignment).filter(
            SeatingAssignment.waitlistID == assignment.waitlistID
        ).first():
            raise HTTPException(
                status_code=400,
                detail=f"Waitlist entry {assignment.waitlistID} already has a seating assignment.",
            )

    # Reservation existence 
    if has_reservation:
        if not db.query(Reservation).filter(
            Reservation.reservationID == assignment.reservationID
        ).first():
            raise HTTPException(
                status_code=404,
                detail=f"Reservation {assignment.reservationID} not found.",
            )

    # Waitlist entry existence + status)
    wl_entry = None
    if has_waitlist:
        wl_entry = (
            db.query(WaitlistEntry)
            .filter(WaitlistEntry.waitlistID == assignment.waitlistID)
            .with_for_update()
            .first()
        )
        if wl_entry is None:
            raise HTTPException(
                status_code=404,
                detail=f"Waitlist entry {assignment.waitlistID} not found.",
            )
        if wl_entry.entryStatus != "Waiting":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Waitlist entry {assignment.waitlistID} cannot be seated — "
                    f"current status is '{wl_entry.entryStatus}' (must be 'Waiting')."
                ),
            )

    # Table existence (with row lock) 
    table = (
        db.query(RestaurantTable)
        .filter(
            RestaurantTable.tableNumber == assignment.tableNumber,
            RestaurantTable.sectionName == assignment.sectionName,
        )
        .with_for_update()
        .first()
    )
    if table is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Table {assignment.tableNumber} in section "
                f"'{assignment.sectionName}' does not exist."
            ),
        )

    # Table availability
    if table.availabilityStatus != "Available":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Table {assignment.tableNumber} in '{assignment.sectionName}' "
                f"is not available — current status is '{table.availabilityStatus}'. "
                f"Only tables with status 'Available' can be assigned."
            ),
        )

    # Commit the transaction
    try:
        new_assignment = SeatingAssignment(
            reservationID=assignment.reservationID,
            waitlistID=assignment.waitlistID,
            sectionName=assignment.sectionName,
            tableNumber=assignment.tableNumber,
            employeeID=assignment.employeeID,
            currentStatus=assignment.currentStatus,
        )
        db.add(new_assignment)

        # Mark table occupied
        table.availabilityStatus = "Occupied"

        # Mark waitlist entry seated
        if wl_entry is not None:
            wl_entry.entryStatus = "Seated"

        db.commit()
        db.refresh(new_assignment)
        return new_assignment

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {exc.orig}",
        )


# GET /seating-assignments/{assignment_id}
@router.get("/{assignment_id}", response_model=SeatingAssignmentResponse)
def get_seating_assignment(assignment_id: int, db: Session = Depends(get_db)):
    obj = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Seating assignment not found.")
    return obj


# PUT /seating-assignments/{assignment_id}
# Completed or Cancelled frees the table back to Available
@router.put("/{assignment_id}", response_model=SeatingAssignmentResponse)
def update_seating_assignment(
    assignment_id: int,
    update: SeatingAssignmentUpdate,
    db: Session = Depends(get_db),
):
    if update.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status '{update.currentStatus}'. "
                f"Allowed values: {sorted(VALID_ASSIGNMENT_STATUSES)}"
            ),
        )

    obj = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Seating assignment not found.")

    old_status = obj.currentStatus
    obj.currentStatus = update.currentStatus

    if update.currentStatus in ("Completed", "Cancelled") and old_status == "Seated":
        table = (
            db.query(RestaurantTable)
            .filter(
                RestaurantTable.tableNumber == obj.tableNumber,
                RestaurantTable.sectionName == obj.sectionName,
            )
            .first()
        )
        if table is not None:
            table.availabilityStatus = "Available"

    db.commit()
    db.refresh(obj)
    return obj


# DELETE /seating-assignments/{assignment_id}
@router.delete("/{assignment_id}")
def delete_seating_assignment(assignment_id: int, db: Session = Depends(get_db)):
    obj = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Seating assignment not found.")
    db.delete(obj)
    db.commit()
    return {"message": "Seating assignment successfully deleted"}