from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bill import Bill
from app.schemas.bill import BillCreate, BillResponse, BillUpdate

# Create a router object to group all bill-related endpoints together
router = APIRouter()


# POST /bills/
# Creates a new bill
@router.post("/", response_model=BillResponse)
def create_bill(
    bill: BillCreate,
    db: Session = Depends(get_db)
) -> Bill:
    # Check whether a bill already exists for this seating assignment
    existing_bill = (
        db.query(Bill)
        .filter(Bill.assignmentID == bill.assignmentID)
        .first()
    )

    # Each seating assignment can only have one bill
    if existing_bill is not None:
        raise HTTPException(
            status_code=400,
            detail="A bill already exists for this seating assignment"
        )

    # Create a new Bill object from the validated request data
    new_bill = Bill(
        promoID=bill.promoID,
        assignmentID=bill.assignmentID,
        totalAmount=bill.totalAmount,
        taxesAndFees=bill.taxesAndFees,
        isSettled=bill.isSettled
    )

    # Add the new bill to the current database session
    db.add(new_bill)

    # Save the new bill row to the database
    db.commit()

    # Refresh the object so the auto-generated invoiceID is available
    db.refresh(new_bill)

    # Return the created bill
    return new_bill


# GET /bills/{invoice_id}
# Retrieves one bill by invoice ID
@router.get("/{invoice_id}", response_model=BillResponse)
def get_bill(
    invoice_id: int,
    db: Session = Depends(get_db)
) -> Bill:
    # Query the database for the bill with this invoice ID
    bill = (
        db.query(Bill)
        .filter(Bill.invoiceID == invoice_id)
        .first()
    )

    # If the bill does not exist, return an HTTP 404 error
    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    # Return the bill if found
    return bill


# PUT /bills/{invoice_id}
# Updates an existing bill
@router.put("/{invoice_id}", response_model=BillResponse)
def update_bill(
    invoice_id: int,
    update: BillUpdate,
    db: Session = Depends(get_db)
) -> Bill:
    # Find the bill by invoice ID
    bill = (
        db.query(Bill)
        .filter(Bill.invoiceID == invoice_id)
        .first()
    )

    # If the bill does not exist, return an HTTP 404 error
    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    # If promoID or totals are being updated, apply the new values
    bill.promoID = update.promoID
    bill.totalAmount = update.totalAmount
    bill.taxesAndFees = update.taxesAndFees
    bill.isSettled = update.isSettled

    # Save the updated bill
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(bill)

    # Return the updated bill
    return bill


# DELETE /bills/{invoice_id}
# Deletes a bill by invoice ID
@router.delete("/{invoice_id}")
def delete_bill(
    invoice_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the bill by invoice ID
    bill = (
        db.query(Bill)
        .filter(Bill.invoiceID == invoice_id)
        .first()
    )

    # If the bill does not exist, return an HTTP 404 error
    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )

    # Delete the bill from the database
    db.delete(bill)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Bill successfully deleted"}