from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class PropertyValueBase(BaseModel):
    property_id: int
    date: date
    valuation: float = Field(..., ge=0)


class PropertyValueCreate(PropertyValueBase):
    pass


class PropertyValueUpdate(BaseModel):
    property_id: Optional[int] = None
    date: Optional[date] = None
    valuation: Optional[float] = Field(None, ge=0)


class PropertyValue(PropertyValueBase):
    property_value_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
