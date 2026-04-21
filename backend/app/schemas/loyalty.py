from pydantic import BaseModel, EmailStr, Field

class LoyaltyCreate(BaseModel):
    email: EmailStr
    # Was Field(gt=0) which means strictly > 0.
    # Changed to ge=0 (greater-than-or-equal) to allow 0-point enrollment.
    pointsBalance: int = Field(ge=0, default=0)


class LoyaltyResponse(BaseModel):
    # Field name matches the SQLAlchemy attribute (LoyaltyID), not the DB column
    LoyaltyID: int
    email: EmailStr
    pointsBalance: int 

    model_config = {"from_attributes": True}