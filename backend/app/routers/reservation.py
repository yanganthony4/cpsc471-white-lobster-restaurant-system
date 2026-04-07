from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr
from datetime import datetime

from app.database import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate

# Create a router object to group all reservation-related endpoints together
router = APIRouter()


# POST /reservation/
# Creates a new reservation
@router.post("/", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
) -> Reservation:
    # Make sure the reservation date/time is in the future
    if reservation.reservationDateTime <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Reservation date and time must be in the future"
        )

    # Make sure the party size is valid
    if reservation.partySize <= 0:
        raise HTTPException(
            status_code=400,
            detail="Party size must be greater than 0"
        )

    # Check whether this customer already has a reservation
    existing_reservation = (
        db.query(Reservation)
        .filter(Reservation.email == reservation.email)
        .first()
    )

    # If a reservation already exists for this email, stop and return an error
    if existing_reservation is not None:
        raise HTTPException(
            status_code=400,
            detail="Each customer is only allowed one reservation at a time"
        )

    # Create a new Reservation object from the validated request data
    new_reservation = Reservation(
        email=reservation.email,
        specialRequests=reservation.specialRequests,
        partySize=reservation.partySize,
        reservationDateTime=reservation.reservationDateTime
    )

    # Add the new reservation to the current database session
    db.add(new_reservation)

    # Save the new reservation row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_reservation)

    # Return the newly created reservation
    return new_reservation


# GET /reservation/{customer_email}
# Retrieves a reservation by customer email
@router.get("/{customer_email}", response_model=ReservationResponse)
def get_reservation(
    customer_email: EmailStr,
    db: Session = Depends(get_db)
) -> Reservation:
    # Look up the reservation matching this customer email
    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )

    # If no reservation is found, return an HTTP 404 error
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    # Return the reservation if found
    return reservation


# PUT /reservation/{customer_email}
# Updates an existing reservation for the given customer email
@router.put("/{customer_email}", response_model=ReservationResponse)
def update_reservation(
    customer_email: EmailStr,
    update: ReservationUpdate,
    db: Session = Depends(get_db)
) -> Reservation:
    # Validate that the updated reservation date/time is still in the future
    if update.reservationDateTime <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Reservation date and time must be in the future"
        )

    # Validate that the updated party size is valid
    if update.partySize <= 0:
        raise HTTPException(
            status_code=400,
            detail="Party size must be greater than 0"
        )

    # Find the reservation that belongs to this customer email
    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )

    # If the reservation does not exist, return an HTTP 404 error
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    # Update the reservation fields using the new request data
    reservation.specialRequests = update.specialRequests
    reservation.partySize = update.partySize
    reservation.reservationDateTime = update.reservationDateTime

    # Save the updated reservation to the database
    db.commit()

    # Refresh the reservation object so it reflects the latest database state
    db.refresh(reservation)

    # Return the updated reservation
    return reservation


# DELETE /reservation/{customer_email}
# Deletes the reservation associated with the given customer email
@router.delete("/{customer_email}")
def delete_reservation_account(
    customer_email: EmailStr,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the reservation matching this customer email
    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )

    # If the reservation does not exist, return an HTTP 404 error
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found"
        )

    # Delete the reservation from the database
    db.delete(reservation)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Reservation successfully deleted"}