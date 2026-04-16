from pydantic import BaseModel, Field


class SectionCreate(BaseModel):
    sectionName: str = Field(min_length=1, max_length=100)
    employeeID: int | None = None


class SectionUpdate(BaseModel):
    employeeID: int | None = None


class SectionResponse(BaseModel):
    sectionName: str
    employeeID: int | None = None

    model_config = {"from_attributes": True}