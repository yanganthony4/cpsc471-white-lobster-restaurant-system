from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.bill import Bill
from app.models.seating_assignment import SeatingAssignment
from app.schemas.bill import BillCreate, BillResponse, BillUpdate

router = APIRouter()


# POST /bills/
@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)) -> Bill:
    # Validate the seating assignment exists before attempting INSERT
    if not db.query(SeatingAssignment).filter(
        SeatingAssignment.assignmentID == bill.assignmentID
    ).first():
        raise HTTPException(
            status_code=404,
            detail=f"Seating assignment {bill.assignmentID} not found.",
        )

    if db.query(Bill).filter(Bill.assignmentID == bill.assignmentID).first():
        raise HTTPException(
            status_code=400,
            detail="A bill already exists for this seating assignment.",
        )

    try:
        new_bill = Bill(
            promoID=bill.promoID,
            assignmentID=bill.assignmentID,
            totalAmount=bill.totalAmount,
            taxesAndFees=bill.taxesAndFees,
            isSettled=bill.isSettled,
        )
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)
        return new_bill
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {exc.orig}",
        )


# GET /bills/{invoice_id}
@router.get("/{invoice_id}", response_model=BillResponse)
def get_bill(invoice_id: int, db: Session = Depends(get_db)) -> Bill:
    bill = db.query(Bill).filter(Bill.invoiceID == invoice_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found.")
    return bill


# PUT /bills/{invoice_id}
@router.put("/{invoice_id}", response_model=BillResponse)
def update_bill(invoice_id: int, update: BillUpdate, db: Session = Depends(get_db)) -> Bill:
    bill = db.query(Bill).filter(Bill.invoiceID == invoice_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found.")
    bill.promoID      = update.promoID
    bill.totalAmount  = update.totalAmount
    bill.taxesAndFees = update.taxesAndFees
    bill.isSettled    = update.isSettled
    db.commit()
    db.refresh(bill)
    return bill


# DELETE /bills/{invoice_id}
@router.delete("/{invoice_id}")
def delete_bill(invoice_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    bill = db.query(Bill).filter(Bill.invoiceID == invoice_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found.")
    db.delete(bill)
    db.commit()
    return {"message": "Bill successfully deleted"}