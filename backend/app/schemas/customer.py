from pydantic import BaseModel, EmailStr

class CustomerCreate(BaseModel):
    email:EmailStr
    phoneNumber: str | None = None
    name: str
    username: str
    password: str

class CustomerLogin(BaseModel):
    username: str
    password: str

class CustomerResponse(BaseModel):
    email:EmailStr
    phoneNumber: str | None = None
    name: str
    username: str

    model_config = {"from_attributes": True}