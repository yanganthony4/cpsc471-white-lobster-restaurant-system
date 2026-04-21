from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.payment import Payment
from app.models.bill import Bill
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate

router = APIRouter()
VALID_PAYMENT_METHODS = {"Cash", "Debit", "Credit", "Gift Card", "Online"}


def _auto_settle(invoice_id: int, db: Session) -> None:
    """Settle the bill automatically once payments cover the total."""
    bill = db.query(Bill).filter(Bill.invoiceID == invoice_id).first()
    if not bill or bill.isSettled:
        return
    total_paid = db.query(func.sum(Payment.amount)).filter(
        Payment.invoiceID == invoice_id
    ).scalar() or 0
    grand_total = (bill.totalAmount or 0) + (bill.taxesAndFees or 0)
    if total_paid >= grand_total:
        bill.isSettled = True


# GET /payments/by-invoice/{invoice_id}  — all payments for a bill
@router.get("/by-invoice/{invoice_id}", response_model=List[PaymentResponse])
def list_payments_for_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.invoiceID == invoice_id).all()


# POST /payments/
@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    if payment.paymentMethod not in VALID_PAYMENT_METHODS:
        raise HTTPException(400, detail="Invalid payment method")

    bill = db.query(Bill).filter(Bill.invoiceID == payment.invoiceID).first()
    if not bill:
        raise HTTPException(404, detail="Bill not found")
    if bill.isSettled:
        raise HTTPException(400, detail="Bill is already settled")

    obj = Payment(
        invoiceID=payment.invoiceID,
        paymentMethod=payment.paymentMethod,
        amount=payment.amount,
    )
    db.add(obj)
    db.flush()                      # persist payment so _auto_settle can sum it
    _auto_settle(payment.invoiceID, db)   # FIX: auto-settle if fully paid
    db.commit()
    db.refresh(obj)
    return obj


# GET /payments/{payment_id}
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.paymentID == payment_id).first()
    if not obj:
        raise HTTPException(404, detail="Payment not found")
    return obj


# PUT /payments/{payment_id}
@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: int, update: PaymentUpdate, db: Session = Depends(get_db)):
    if update.paymentMethod not in VALID_PAYMENT_METHODS:
        raise HTTPException(400, detail="Invalid payment method")
    obj = db.query(Payment).filter(Payment.paymentID == payment_id).first()
    if not obj:
        raise HTTPException(404, detail="Payment not found")
    obj.paymentMethod = update.paymentMethod
    obj.amount = update.amount
    _auto_settle(obj.invoiceID, db)
    db.commit(); db.refresh(obj)
    return obj


# DELETE /payments/{payment_id}
@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    obj = db.query(Payment).filter(Payment.paymentID == payment_id).first()
    if not obj:
        raise HTTPException(404, detail="Payment not found")
    db.delete(obj); db.commit()
    return {"message": "Payment successfully deleted"}