from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr
from datetime import datetime, timezone

from app.database import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate

router = APIRouter()


def _to_utc(dt: datetime) -> datetime:
    #FIX: Timezone-strip bug.
   
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


router = APIRouter()


# POST /reservation/
@router.post("/", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
) -> Reservation:
    if _to_utc(reservation.reservationDateTime) <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reservation date and time must be in the future")

    if reservation.partySize <= 0:
        raise HTTPException(status_code=400, detail="Party size must be greater than 0")

    existing = (
        db.query(Reservation)
        .filter(Reservation.email == reservation.email)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Each customer is only allowed one reservation at a time")

    new_reservation = Reservation(
        email=reservation.email,
        specialRequests=reservation.specialRequests,
        partySize=reservation.partySize,
        reservationDateTime=_to_utc(reservation.reservationDateTime),
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


# GET /reservation/{customer_email}
@router.get("/{customer_email}", response_model=ReservationResponse)
def get_reservation(
    customer_email: EmailStr,
    db: Session = Depends(get_db),
) -> Reservation:
    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


# PUT /reservation/{customer_email}
@router.put("/{customer_email}", response_model=ReservationResponse)
def update_reservation(
    customer_email: EmailStr,
    update: ReservationUpdate,
    db: Session = Depends(get_db),
) -> Reservation:
    if _to_utc(update.reservationDateTime) <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reservation date and time must be in the future")

    if update.partySize <= 0:
        raise HTTPException(status_code=400, detail="Party size must be greater than 0")

    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.specialRequests     = update.specialRequests
    reservation.partySize           = update.partySize
    reservation.reservationDateTime = _to_utc(update.reservationDateTime)

    db.commit()
    db.refresh(reservation)
    return reservation


# DELETE /reservation/{customer_email}
@router.delete("/{customer_email}")
def delete_reservation(
    customer_email: EmailStr,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    reservation = (
        db.query(Reservation)
        .filter(Reservation.email == customer_email)
        .first()
    )
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    db.delete(reservation)
    db.commit()
    return {"message": "Reservation successfully deleted"}