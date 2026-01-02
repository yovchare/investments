from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PropertyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class Property(PropertyBase):
    property_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
