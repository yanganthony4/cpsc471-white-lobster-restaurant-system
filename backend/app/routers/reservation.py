from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate

router = APIRouter()


def _strip_tz(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


# GET /reservation/  — LIST ALL (staff use)
@router.get("/", response_model=List[ReservationResponse])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.reservationID).all()


# POST /reservation/
@router.post("/", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    if _strip_tz(reservation.reservationDateTime) <= datetime.utcnow():
        raise HTTPException(400, detail="Reservation date and time must be in the future")
    existing = db.query(Reservation).filter(Reservation.email == reservation.email).first()
    if existing:
        raise HTTPException(400, detail="Each customer is only allowed one reservation at a time")
    obj = Reservation(
        email=reservation.email,
        specialRequests=reservation.specialRequests,
        partySize=reservation.partySize,
        reservationDateTime=_strip_tz(reservation.reservationDateTime),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# GET /reservation/{customer_email}
@router.get("/{customer_email}", response_model=ReservationResponse)
def get_reservation(customer_email: str, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.email == customer_email).first()
    if not r:
        raise HTTPException(404, detail="Reservation not found")
    return r


# PUT /reservation/{customer_email}
@router.put("/{customer_email}", response_model=ReservationResponse)
def update_reservation(customer_email: str, update: ReservationUpdate, db: Session = Depends(get_db)):
    if _strip_tz(update.reservationDateTime) <= datetime.utcnow():
        raise HTTPException(400, detail="Reservation date and time must be in the future")
    r = db.query(Reservation).filter(Reservation.email == customer_email).first()
    if not r:
        raise HTTPException(404, detail="Reservation not found")
    r.specialRequests = update.specialRequests
    r.partySize = update.partySize
    r.reservationDateTime = _strip_tz(update.reservationDateTime)
    db.commit(); db.refresh(r)
    return r


# DELETE /reservation/{customer_email}
@router.delete("/{customer_email}")
def delete_reservation(customer_email: str, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.email == customer_email).first()
    if not r:
        raise HTTPException(404, detail="Reservation not found")
    db.delete(r); db.commit()
    return {"message": "Reservation successfully deleted"}