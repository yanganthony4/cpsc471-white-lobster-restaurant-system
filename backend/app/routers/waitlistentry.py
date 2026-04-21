from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.waitlistentry import WaitlistEntry
from app.schemas.waitlistentry import (
    WaitlistEntryCreate, WaitlistEntryUpdate, WaitlistStatusUpdate, WaitlistResponse,
)

router = APIRouter()
VALID_STATUSES = {"Waiting", "Seated", "Cancelled", "Removed"}


# GET /waitlist/?status=Waiting   — returns full queue, filterable
@router.get("/", response_model=List[WaitlistResponse])
def list_waitlist_entries(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(WaitlistEntry)
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(400, detail="Invalid status filter")
        q = q.filter(WaitlistEntry.entryStatus == status)
    return q.order_by(WaitlistEntry.joinTime).all()


# POST /waitlist/
@router.post("/", response_model=WaitlistResponse)
def create_waitlist_entry(waitlist_entry: WaitlistEntryCreate, db: Session = Depends(get_db)):
    existing = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == waitlist_entry.email,
        WaitlistEntry.entryStatus == "Waiting",
    ).first()
    if existing:
        raise HTTPException(400, detail="Customer already has an active waitlist entry")
    obj = WaitlistEntry(
        email=waitlist_entry.email,
        specialRequests=waitlist_entry.specialRequests,
        partySize=waitlist_entry.partySize,
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# GET /waitlist/{customer_email}  — returns the active (Waiting) entry
@router.get("/{customer_email}", response_model=WaitlistResponse)
def get_waitlist_entry(customer_email: str, db: Session = Depends(get_db)):
    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == customer_email,
        WaitlistEntry.entryStatus == "Waiting",
    ).order_by(WaitlistEntry.joinTime.desc()).first()
    if entry is None:
        entry = db.query(WaitlistEntry).filter(
            WaitlistEntry.email == customer_email
        ).order_by(WaitlistEntry.joinTime.desc()).first()
    if entry is None:
        raise HTTPException(404, detail="Waitlist entry not found")
    return entry


# PUT /waitlist/{customer_email}  — update party size / requests on active entry
@router.put("/{customer_email}", response_model=WaitlistResponse)
def update_waitlist_entry(customer_email: str, update: WaitlistEntryUpdate, db: Session = Depends(get_db)):
    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == customer_email, WaitlistEntry.entryStatus == "Waiting",
    ).first()
    if not entry:
        raise HTTPException(404, detail="Active waitlist entry not found")
    entry.specialRequests = update.specialRequests
    entry.partySize = update.partySize
    db.commit(); db.refresh(entry)
    return entry


# PATCH /waitlist/{waitlist_id}/status  — staff changes status (Seated, Removed, etc.)
@router.patch("/{waitlist_id}/status", response_model=WaitlistResponse)
def update_waitlist_status(waitlist_id: int, update: WaitlistStatusUpdate, db: Session = Depends(get_db)):
    if update.entryStatus not in VALID_STATUSES:
        raise HTTPException(400, detail="Invalid waitlist status")
    entry = db.query(WaitlistEntry).filter(WaitlistEntry.waitlistID == waitlist_id).first()
    if not entry:
        raise HTTPException(404, detail="Waitlist entry not found")
    entry.entryStatus = update.entryStatus
    db.commit(); db.refresh(entry)
    return entry


# DELETE /waitlist/{customer_email}
@router.delete("/{customer_email}")
def delete_waitlist_entry(customer_email: str, db: Session = Depends(get_db)):
    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == customer_email
    ).order_by(WaitlistEntry.joinTime.desc()).first()
    if not entry:
        raise HTTPException(404, detail="Waitlist entry not found")
    db.delete(entry); db.commit()
    return {"message": "Waitlist entry successfully deleted"}