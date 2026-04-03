from pydantic import BaseModel, Field


class StaffCreate(BaseModel):
    employeeID: int
    role: str
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=255)


class StaffLogin(BaseModel):
    employeeID: int
    password: str = Field(min_length=8, max_length=255)


class StaffUpdate(BaseModel):
    role: str
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=255)


class StaffResponse(BaseModel):
    employeeID: int
    role: str
    name: str

    model_config = {"from_attributes": True}