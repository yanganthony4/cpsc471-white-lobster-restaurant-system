from decimal import Decimal

from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    description: str | None = None
    currentPrice: Decimal = Field(ge=0)
    name: str = Field(min_length=1, max_length=100)


class MenuItemUpdate(BaseModel):
    description: str | None = None
    currentPrice: Decimal = Field(ge=0)
    name: str = Field(min_length=1, max_length=100)


class MenuItemResponse(BaseModel):
    menuItemID: int
    description: str | None = None
    currentPrice: Decimal
    name: str

    model_config = {"from_attributes": True}