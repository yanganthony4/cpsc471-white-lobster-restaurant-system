from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.models.loyalty import LoyaltyProgram
from app.schemas.loyalty import LoyaltyCreate, LoyaltyResponse

router = APIRouter()


# POST /loyalty/
@router.post("/", response_model=LoyaltyResponse)
def create_loyalty_account(
    loyalty: LoyaltyCreate,
    db: Session = Depends(get_db),
) -> LoyaltyProgram:
    existing = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == loyalty.email)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Loyalty account already exists for this customer")

    new_loyalty = LoyaltyProgram(
        email=loyalty.email,
        # now ge=0, so 0 is valid on enrollment
        pointsBalance=loyalty.pointsBalance,
    )
    db.add(new_loyalty)
    db.commit()
    db.refresh(new_loyalty)
    return new_loyalty


# GET /loyalty/{customer_email}
@router.get("/{customer_email}", response_model=LoyaltyResponse)
def get_loyalty_account(
    customer_email: EmailStr,
    db: Session = Depends(get_db),
) -> LoyaltyProgram:
    account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Loyalty account not found")
    return account


# Added explicit type annotation so FastAPI doesn't reject it as a missing body.
@router.put("/{customer_email}", response_model=LoyaltyResponse)
def update_loyalty_account(
    customer_email: EmailStr,
    points_balance: int,
    db: Session = Depends(get_db),
) -> LoyaltyProgram:
    if points_balance < 0:
        raise HTTPException(status_code=400, detail="Points balance cannot be negative")

    account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    account.pointsBalance = points_balance
    db.commit()
    db.refresh(account)
    return account


# DELETE /loyalty/{customer_email}
@router.delete("/{customer_email}")
def delete_loyalty_account(
    customer_email: EmailStr,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    account = (
        db.query(LoyaltyProgram)
        .filter(LoyaltyProgram.email == customer_email)
        .first()
    )
    if account is None:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    db.delete(account)
    db.commit()
    return {"message": "Loyalty account successfully deleted"}