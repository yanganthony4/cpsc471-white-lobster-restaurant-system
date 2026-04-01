from pydantic import BaseModel, Field


class StaffCreate(BaseModel):
    role: str
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=255)


class StaffLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=255)


class StaffResponse(BaseModel):
    employeeID: int
    role: str
    name: str
    username: str

    model_config = {"from_attributes": True}