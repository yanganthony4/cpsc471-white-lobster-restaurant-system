from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate

# Create a router object to group all payment-related endpoints together
router = APIRouter()

# Allowed payment methods based on the database CHECK constraint
VALID_PAYMENT_METHODS = {"Cash", "Debit", "Credit", "Gift Card", "Online"}


# POST /payments/
# Creates a new payment
@router.post("/", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
) -> Payment:
    # Validate the payment method against the allowed values
    if payment.paymentMethod not in VALID_PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method"
        )

    # Create a new Payment object from the validated request data
    new_payment = Payment(
        invoiceID=payment.invoiceID,
        paymentMethod=payment.paymentMethod,
        amount=payment.amount
    )

    # Add the new payment to the current database session
    db.add(new_payment)

    # Save the new row to the database
    db.commit()

    # Refresh the object so the auto-generated paymentID and timestamp are available
    db.refresh(new_payment)

    # Return the created payment
    return new_payment


# GET /payments/{payment_id}
# Retrieves one payment by payment ID
@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
) -> Payment:
    # Query the database for the payment with this payment ID
    payment = (
        db.query(Payment)
        .filter(Payment.paymentID == payment_id)
        .first()
    )

    # If the payment does not exist, return an HTTP 404 error
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    # Return the payment if found
    return payment


# PUT /payments/{payment_id}
# Updates an existing payment
@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    update: PaymentUpdate,
    db: Session = Depends(get_db)
) -> Payment:
    # Validate the updated payment method
    if update.paymentMethod not in VALID_PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method"
        )

    # Find the payment by payment ID
    payment = (
        db.query(Payment)
        .filter(Payment.paymentID == payment_id)
        .first()
    )

    # If the payment does not exist, return an HTTP 404 error
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    # Apply the updated values
    payment.paymentMethod = update.paymentMethod
    payment.amount = update.amount

    # Save the updated payment
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(payment)

    # Return the updated payment
    return payment


# DELETE /payments/{payment_id}
# Deletes a payment by payment ID
@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the payment by payment ID
    payment = (
        db.query(Payment)
        .filter(Payment.paymentID == payment_id)
        .first()
    )

    # If the payment does not exist, return an HTTP 404 error
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    # Delete the payment from the database
    db.delete(payment)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Payment successfully deleted"}