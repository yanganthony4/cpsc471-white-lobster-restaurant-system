from pydantic import BaseModel, Field


class RestaurantTableCreate(BaseModel):
    tableNumber: int
    sectionName: str = Field(min_length=1, max_length=100)
    availabilityStatus: str = "Available"
    capacity: int = Field(gt=0)


class RestaurantTableUpdate(BaseModel):
    availabilityStatus: str
    capacity: int = Field(gt=0)


class RestaurantTableResponse(BaseModel):
    tableNumber: int
    sectionName: str
    availabilityStatus: str
    capacity: int

    model_config = {"from_attributes": True}