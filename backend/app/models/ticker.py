from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


# Ticker symbols that the user wants to track
class TickerBase(BaseModel):
    ticker_symbol: str = Field(..., min_length=1, max_length=10)


class TickerCreate(TickerBase):
    pass


class TickerUpdate(BaseModel):
    ticker_symbol: Optional[str] = Field(None, min_length=1, max_length=10)


class Ticker(TickerBase):
    ticker_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Price data for tickers
class TickerPriceBase(BaseModel):
    ticker_id: int
    date: date
    price: float = Field(..., gt=0)


class TickerPriceCreate(TickerPriceBase):
    pass


class TickerPriceUpdate(BaseModel):
    ticker_id: Optional[int] = None
    date: Optional[date] = None
    price: Optional[float] = Field(None, gt=0)


class TickerPrice(TickerPriceBase):
    price_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
