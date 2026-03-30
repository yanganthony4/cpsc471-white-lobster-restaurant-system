from pydantic import BaseModel, EmailStr

# Determines the format creating loyalty account
class LoyaltyCreate(BaseModel):
    email: EmailStr
    pointsBalance: int

class LoyaltyUpdate(BaseModel):
    pointsBalance: int

# Determines response of loyalty account
class LoyaltyResponse(BaseModel):
    Loyalty_id: int
    email: EmailStr
    pointsBalance: int

    model_config = {"from_attributes": True}

