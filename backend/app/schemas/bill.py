from decimal import Decimal

from pydantic import BaseModel, Field


class BillCreate(BaseModel):
    promoID: int | None = None
    assignmentID: int
    totalAmount: Decimal = Field(ge=0)
    taxesAndFees: Decimal = Field(ge=0)
    isSettled: bool = False


class BillUpdate(BaseModel):
    promoID: int | None = None
    totalAmount: Decimal = Field(ge=0)
    taxesAndFees: Decimal = Field(ge=0)
    isSettled: bool


class BillResponse(BaseModel):
    invoiceID: int
    promoID: int | None = None
    assignmentID: int
    totalAmount: Decimal
    taxesAndFees: Decimal
    isSettled: bool

    model_config = {"from_attributes": True}