from pydantic import BaseModel, EmailStr, Field
from datetime import time

class WaitlistEntryCreate(BaseModel):
    email: EmailStr
    specialRequests: str | None = None
    partySize: int = Field(gt=0)

class WaitlistEntryUpdate(BaseModel):
    specialRequests: str | None = None
    partySize: int = Field(gt=0)

class WaitlistResponse(BaseModel):
    waitlistID: int 
    email: EmailStr
    specialRequests: str | None = None
    entryStatus: str
    joinTime: time
    partySize: int 
    estimatedWaitTime: int

    model_config = {"from_attributes": True}
