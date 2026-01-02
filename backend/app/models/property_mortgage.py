from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class PropertyMortgageBase(BaseModel):
    property_id: int
    date: date
    mortgage: float = Field(..., ge=0)


class PropertyMortgageCreate(PropertyMortgageBase):
    pass


class PropertyMortgageUpdate(BaseModel):
    property_id: Optional[int] = None
    date: Optional[date] = None
    mortgage: Optional[float] = Field(None, ge=0)


class PropertyMortgage(PropertyMortgageBase):
    property_mortgage_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
