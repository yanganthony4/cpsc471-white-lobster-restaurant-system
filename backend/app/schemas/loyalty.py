from pydantic import BaseModel, EmailStr, Field

# Determines the format creating loyalty account
class LoyaltyCreate(BaseModel):
    email: EmailStr
    pointsBalance: int = Field(gt=0)

# Determines response of loyalty account
class LoyaltyResponse(BaseModel):
    Loyalty_id: int
    email: EmailStr
    pointsBalance: int 

    model_config = {"from_attributes": True}

