from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PromotionCreate(BaseModel):
    startDate: date
    endDate: date
    discountAmount: Decimal = Field(ge=0)
    eligibilityRules: str | None = None


class PromotionUpdate(BaseModel):
    startDate: date
    endDate: date
    discountAmount: Decimal = Field(ge=0)
    eligibilityRules: str | None = None


class PromotionResponse(BaseModel):
    promoID: int
    startDate: date
    endDate: date
    discountAmount: Decimal
    eligibilityRules: str | None = None

    model_config = {"from_attributes": True}