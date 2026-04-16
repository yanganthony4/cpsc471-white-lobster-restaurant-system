from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.models.waitlistentry import WaitlistEntry
from app.schemas.waitlistentry import (
    WaitlistEntryCreate,
    WaitlistEntryUpdate,
    WaitlistResponse,
)

router = APIRouter()


# POST /waitlist/
# Creates a new waitlist entry
@router.post("/", response_model=WaitlistResponse)
def create_waitlist_entry(
    waitlist_entry: WaitlistEntryCreate,
    db: Session = Depends(get_db)
) -> WaitlistEntry:
    if waitlist_entry.partySize <= 0:
        raise HTTPException(
            status_code=400,
            detail="Party size must be greater than 0"
        )

    # Check whether this customer already has a waitlist entry
    existing_waitlist_entry = (
        db.query(WaitlistEntry)
        .filter(WaitlistEntry.email == waitlist_entry.email)
        .first()
    )

    if existing_waitlist_entry is not None:
        raise HTTPException(
            status_code=400,
            detail="Customer already has a waitlist entry"
        )

    new_waitlist_entry = WaitlistEntry(
        email=waitlist_entry.email,
        specialRequests=waitlist_entry.specialRequests,
        partySize=waitlist_entry.partySize
    )

    db.add(new_waitlist_entry)
    db.commit()
    db.refresh(new_waitlist_entry)

    return new_waitlist_entry


# GET /waitlist/{customer_email}
# Retrieves a waitlist entry by customer email
@router.get("/{customer_email}", response_model=WaitlistResponse)
def get_waitlist_entry(
    customer_email: EmailStr,
    db: Session = Depends(get_db)
) -> WaitlistEntry:
    waitlist_entry = (
        db.query(WaitlistEntry)
        .filter(WaitlistEntry.email == customer_email)
        .first()
    )

    if waitlist_entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found"
        )

    return waitlist_entry


# PUT /waitlist/{customer_email}
# Updates an existing waitlist entry by customer email
@router.put("/{customer_email}", response_model=WaitlistResponse)
def update_waitlist_entry(
    customer_email: EmailStr,
    update: WaitlistEntryUpdate,
    db: Session = Depends(get_db)
) -> WaitlistEntry:
    if update.partySize <= 0:
        raise HTTPException(
            status_code=400,
            detail="Party size must be greater than 0"
        )

    waitlist_entry = (
        db.query(WaitlistEntry)
        .filter(WaitlistEntry.email == customer_email)
        .first()
    )

    if waitlist_entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found"
        )

    waitlist_entry.specialRequests = update.specialRequests
    waitlist_entry.partySize = update.partySize

    db.commit()
    db.refresh(waitlist_entry)

    return waitlist_entry


# DELETE /waitlist/{customer_email}
# Deletes a waitlist entry by customer email
@router.delete("/{customer_email}")
def delete_waitlist_entry(
    customer_email: EmailStr,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    waitlist_entry = (
        db.query(WaitlistEntry)
        .filter(WaitlistEntry.email == customer_email)
        .first()
    )

    if waitlist_entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found"
        )

    db.delete(waitlist_entry)
    db.commit()

    return {"message": "Waitlist entry successfully deleted"}