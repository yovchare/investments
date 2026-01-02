from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccountBase(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class Account(AccountBase):
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
