from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.models.loyalty import LoyaltyProgram
from app.schemas.loyalty import LoyaltyCreate, LoyaltyResponse

# Create a router object to group all loyalty-related endpoints together
router = APIRouter()

# POST /loyalty/
# Creates a new loyalty account
@router.post("/", response_model=LoyaltyResponse)
def create_loyalty_account(
    loyalty: LoyaltyCreate,
    db: Session = Depends(get_db)
) -> LoyaltyProgram:
    # Check whether a loyalty account already exists for this customer email
    existing_loyalty = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == loyalty.email)
        .first()
    )

    # If an account already exists, stop the function and return an HTTP 400 error
    if existing_loyalty is not None:
        raise HTTPException(
            status_code=400,
            detail="Loyalty account already exists for this customer"
        )

    # Create a new LoyaltyProgram object using the validated request data
    new_loyalty = LoyaltyProgram(
        email=loyalty.email,
        pointsBalance=loyalty.pointsBalance,
    )

    # Add the new loyalty object to the current database session
    db.add(new_loyalty)

    # Save the new row to the database
    db.commit()

    # Refresh the object so it includes any database-generated values, such as Loyalty_id
    db.refresh(new_loyalty)

    # Return the newly created loyalty account as the response
    return new_loyalty


# GET /loyalty/{customer_email}
# Retrieves a loyalty account by customer email
@router.get("/{customer_email}", response_model=LoyaltyResponse)
def get_loyalty_account(
    customer_email: EmailStr,
    db: Session = Depends(get_db)
) -> LoyaltyProgram:
    # Query the database for the loyalty account with this customer email
    loyalty_account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )

    # If no loyalty account is found, return an HTTP 404 error
    if loyalty_account is None:
        raise HTTPException(
            status_code=404,
            detail="Loyalty account not found"
        )

    # Return the loyalty account if found
    return loyalty_account


# PUT /loyalty/{customer_email}
# Updates the points balance of an existing loyalty account
@router.put("/{customer_email}", response_model=LoyaltyResponse)
def update_loyalty_account(
    customer_email: EmailStr,
    points_balance: int,
    db: Session = Depends(get_db)
) -> LoyaltyProgram:
    # Reject invalid point balances before doing any database update
    if points_balance < 0:
        raise HTTPException(
            status_code=400,
            detail="Points balance cannot be negative"
        )

    # Query the database for the loyalty account matching this customer email
    loyalty_account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )

    # If the loyalty account does not exist, return an HTTP 404 error
    if loyalty_account is None:
        raise HTTPException(
            status_code=404,
            detail="Loyalty account not found"
        )

    # Update the points balance with the new value from the request body
    loyalty_account.pointsBalance = points_balance

    # Save the updated value to the database
    db.commit()

    # Refresh the object so the returned data matches what is in the database
    db.refresh(loyalty_account)

    # Return the updated loyalty account
    return loyalty_account

# DELETE /loyalty/{customer_email}
# Deletes loyalty account
@router.delete("/{customer_email}")
def delete_loyalty_account(
    customer_email:EmailStr,
    db: Session = Depends(get_db)
) -> dict[str,str]:
    # Query the database for the loyalty account matching this customer email
    loyalty_account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )

    # If the loyalty account does not exist, return an HTTP 404 error
    if loyalty_account is None:
        raise HTTPException(
            status_code=404,
            detail="Loyalty account not found"
        )
    
    db.delete(loyalty_account)
    db.commit()

    return {"message": "Loyalty Account successfully deleted"}