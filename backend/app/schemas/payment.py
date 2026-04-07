from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    invoiceID: int
    paymentMethod: str
    amount: Decimal = Field(gt=0)


class PaymentUpdate(BaseModel):
    paymentMethod: str
    amount: Decimal = Field(gt=0)


class PaymentResponse(BaseModel):
    paymentID: int
    invoiceID: int
    paymentMethod: str
    timeStamp: datetime
    amount: Decimal

    model_config = {"from_attributes": True}