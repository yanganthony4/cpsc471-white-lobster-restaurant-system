from pydantic import BaseModel, EmailStr

class CustomerCreate(BaseModel):
    email: EmailStr
    phoneNumber: str | None = None
    name: str
    password: str

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class CustomerUpdate(BaseModel):
    email: EmailStr
    name: str
    phoneNumber: str | None = None
    password: str

class CustomerResponse(BaseModel):
    email: EmailStr
    phoneNumber: str | None = None
    name: str

    model_config = {"from_attributes": True}