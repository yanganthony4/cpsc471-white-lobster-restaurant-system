from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.promotion import Promotion
from app.schemas.promotion import (
    PromotionCreate,
    PromotionUpdate,
    PromotionResponse,
)

# Create a router object to group all promotion-related endpoints together
router = APIRouter()


# POST /promotions/
# Creates a new promotion
@router.post("/", response_model=PromotionResponse)
def create_promotion(
    promotion: PromotionCreate,
    db: Session = Depends(get_db)
) -> Promotion:
    # Make sure the promotion end date is not before the start date
    if promotion.endDate < promotion.startDate:
        raise HTTPException(
            status_code=400,
            detail="Promotion end date cannot be before start date"
        )

    # Create a new Promotion object from the validated request data
    new_promotion = Promotion(
        startDate=promotion.startDate,
        endDate=promotion.endDate,
        discountAmount=promotion.discountAmount,
        eligibilityRules=promotion.eligibilityRules
    )

    # Add the new promotion to the current database session
    db.add(new_promotion)

    # Save the new promotion row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_promotion)

    # Return the created promotion
    return new_promotion


# GET /promotions/{promo_id}
# Retrieves one promotion by promo ID
@router.get("/{promo_id}", response_model=PromotionResponse)
def get_promotion(
    promo_id: int,
    db: Session = Depends(get_db)
) -> Promotion:
    # Query the database for the promotion with this promo ID
    promotion = (
        db.query(Promotion)
        .filter(Promotion.promoID == promo_id)
        .first()
    )

    # If the promotion does not exist, return an HTTP 404 error
    if promotion is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    # Return the promotion if found
    return promotion


# PUT /promotions/{promo_id}
# Updates an existing promotion
@router.put("/{promo_id}", response_model=PromotionResponse)
def update_promotion(
    promo_id: int,
    update: PromotionUpdate,
    db: Session = Depends(get_db)
) -> Promotion:
    # Make sure the updated end date is not before the start date
    if update.endDate < update.startDate:
        raise HTTPException(
            status_code=400,
            detail="Promotion end date cannot be before start date"
        )

    # Find the promotion by promo ID
    promotion = (
        db.query(Promotion)
        .filter(Promotion.promoID == promo_id)
        .first()
    )

    # If the promotion does not exist, return an HTTP 404 error
    if promotion is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    # Apply the updated values
    promotion.startDate = update.startDate
    promotion.endDate = update.endDate
    promotion.discountAmount = update.discountAmount
    promotion.eligibilityRules = update.eligibilityRules

    # Save the updated promotion
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(promotion)

    # Return the updated promotion
    return promotion


# DELETE /promotions/{promo_id}
# Deletes a promotion by promo ID
@router.delete("/{promo_id}")
def delete_promotion(
    promo_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the promotion by promo ID
    promotion = (
        db.query(Promotion)
        .filter(Promotion.promoID == promo_id)
        .first()
    )

    # If the promotion does not exist, return an HTTP 404 error
    if promotion is None:
        raise HTTPException(
            status_code=404,
            detail="Promotion not found"
        )

    # Delete the promotion from the database
    db.delete(promotion)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Promotion successfully deleted"}