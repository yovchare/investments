from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class OwnershipStatus(str, Enum):
    OWNED = "Owned"
    UNOWNED = "Unowned"
    UNVESTED = "Unvested"


class AccountHoldingBase(BaseModel):
    account_id: int
    date: date
    ticker_symbol: str = Field(..., min_length=1, max_length=10)
    number_of_shares: float = Field(..., ge=0)
    value: float = Field(..., ge=0)
    ownership: OwnershipStatus


class AccountHoldingCreate(AccountHoldingBase):
    pass


class AccountHoldingUpdate(BaseModel):
    account_id: Optional[int] = None
    date: Optional[date] = None
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    number_of_shares: Optional[float] = Field(None, ge=0)
    value: Optional[float] = Field(None, ge=0)
    ownership: Optional[OwnershipStatus] = None


class AccountHolding(AccountHoldingBase):
    holding_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
