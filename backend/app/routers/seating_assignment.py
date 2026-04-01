from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.seating_assignment import SeatingAssignment
from app.schemas.seating_assignment import (
    SeatingAssignmentCreate,
    SeatingAssignmentUpdate,
    SeatingAssignmentResponse,
)

# Create a router object to group all seating assignment endpoints together
router = APIRouter()

# Allowed status values for seating assignments
VALID_ASSIGNMENT_STATUSES = {"Seated", "Completed", "Cancelled"}


# POST /seating-assignments/
# Creates a new seating assignment
@router.post("/", response_model=SeatingAssignmentResponse)
def create_seating_assignment(
    assignment: SeatingAssignmentCreate,
    db: Session = Depends(get_db)
) -> SeatingAssignment:
    # Validate the current status value
    if assignment.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid seating assignment status"
        )

    # Enforce the same XOR rule as the database:
    # exactly one of reservationID or waitlistID must be provided
    if (assignment.reservationID is None and assignment.waitlistID is None) or (
        assignment.reservationID is not None and assignment.waitlistID is not None
    ):
        raise HTTPException(
            status_code=400,
            detail="Exactly one of reservationID or waitlistID must be provided"
        )

    # If a reservationID is provided, make sure it is not already assigned
    if assignment.reservationID is not None:
        existing_reservation_assignment = (
            db.query(SeatingAssignment)
            .filter(SeatingAssignment.reservationID == assignment.reservationID)
            .first()
        )

        if existing_reservation_assignment is not None:
            raise HTTPException(
                status_code=400,
                detail="This reservation already has a seating assignment"
            )

    # If a waitlistID is provided, make sure it is not already assigned
    if assignment.waitlistID is not None:
        existing_waitlist_assignment = (
            db.query(SeatingAssignment)
            .filter(SeatingAssignment.waitlistID == assignment.waitlistID)
            .first()
        )

        if existing_waitlist_assignment is not None:
            raise HTTPException(
                status_code=400,
                detail="This waitlist entry already has a seating assignment"
            )

    # Create a new SeatingAssignment object from the validated request data
    new_assignment = SeatingAssignment(
        reservationID=assignment.reservationID,
        waitlistID=assignment.waitlistID,
        sectionName=assignment.sectionName,
        tableNumber=assignment.tableNumber,
        employeeID=assignment.employeeID,
        currentStatus=assignment.currentStatus
    )

    # Add the new seating assignment to the database session
    db.add(new_assignment)

    # Save the new row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_assignment)

    # Return the created seating assignment
    return new_assignment


# GET /seating-assignments/{assignment_id}
# Retrieves one seating assignment by assignment ID
@router.get("/{assignment_id}", response_model=SeatingAssignmentResponse)
def get_seating_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
) -> SeatingAssignment:
    # Find the seating assignment by its primary key
    assignment = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )

    # If it does not exist, return an HTTP 404 error
    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Seating assignment not found"
        )

    # Return the assignment if found
    return assignment


# PUT /seating-assignments/{assignment_id}
# Updates the current status of a seating assignment
@router.put("/{assignment_id}", response_model=SeatingAssignmentResponse)
def update_seating_assignment(
    assignment_id: int,
    update: SeatingAssignmentUpdate,
    db: Session = Depends(get_db)
) -> SeatingAssignment:
    # Validate the updated status value
    if update.currentStatus not in VALID_ASSIGNMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid seating assignment status"
        )

    # Find the seating assignment by ID
    assignment = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )

    # If it does not exist, return an HTTP 404 error
    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Seating assignment not found"
        )

    # Update the status field
    assignment.currentStatus = update.currentStatus

    # Save the updated row
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(assignment)

    # Return the updated assignment
    return assignment


# DELETE /seating-assignments/{assignment_id}
# Deletes a seating assignment by ID
@router.delete("/{assignment_id}")
def delete_seating_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the seating assignment by ID
    assignment = (
        db.query(SeatingAssignment)
        .filter(SeatingAssignment.assignmentID == assignment_id)
        .first()
    )

    # If it does not exist, return an HTTP 404 error
    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Seating assignment not found"
        )

    # Delete the seating assignment
    db.delete(assignment)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Seating assignment successfully deleted"}