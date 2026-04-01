from decimal import Decimal

from pydantic import BaseModel, Field


class BillItemCreate(BaseModel):
    invoiceID: int
    menuItemID: int
    quantity: int = Field(gt=0)
    priceAtOrder: Decimal = Field(ge=0)


class BillItemUpdate(BaseModel):
    quantity: int = Field(gt=0)
    priceAtOrder: Decimal = Field(ge=0)


class BillItemResponse(BaseModel):
    invoiceID: int
    menuItemID: int
    quantity: int
    priceAtOrder: Decimal

    model_config = {"from_attributes": True}