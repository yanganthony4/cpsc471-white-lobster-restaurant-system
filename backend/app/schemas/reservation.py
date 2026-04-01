from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ReservationCreate(BaseModel):
    email: EmailStr
    specialRequests: str | None = None
    partySize: int = Field(gt=0)
    reservationDateTime: datetime

class ReservationUpdate(BaseModel):
    specialRequests: str | None = None
    partySize: int = Field(gt=0)
    reservationDateTime: datetime

class ReservationResponse(BaseModel):
    reservationID: int
    email: EmailStr
    specialRequests: str | None = None
    partySize: int 
    reservationDateTime: datetime

    model_config = {"from_attributes": True}
