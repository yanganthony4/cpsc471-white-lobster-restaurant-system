from pydantic import BaseModel, EmailStr, Field
from datetime import datetime 


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
    # Using Python `time` meant the response contained no date
    joinTime: datetime
    partySize: int
    estimatedWaitTime: int

    model_config = {"from_attributes": True}