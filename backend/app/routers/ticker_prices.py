from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.ticker import TickerPrice, TickerPriceCreate, TickerPriceUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/ticker-prices", tags=["ticker_prices"])


@router.get("/", response_model=List[TickerPrice])
def get_ticker_prices(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all ticker prices"""
    result = db.execute(
        "SELECT * FROM ticker_prices ORDER BY date DESC"
    ).fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/ticker/{ticker_id}", response_model=List[TickerPrice])
def get_prices_for_ticker(ticker_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all prices for a specific ticker"""
    result = db.execute(
        "SELECT * FROM ticker_prices WHERE ticker_id = ? ORDER BY date DESC",
        [ticker_id]
    ).fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{price_id}", response_model=TickerPrice)
def get_ticker_price(price_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific ticker price by ID"""
    result = db.execute(
        "SELECT * FROM ticker_prices WHERE price_id = ?",
        [price_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticker price not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=TickerPrice, status_code=201)
def create_ticker_price(price: TickerPriceCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Create a new ticker price"""
    now = datetime.now()
    
    # Check if ticker exists
    ticker_exists = db.execute(
        "SELECT ticker_id FROM tickers WHERE ticker_id = ?",
        [price.ticker_id]
    ).fetchone()
    
    if not ticker_exists:
        raise HTTPException(status_code=404, detail="Ticker not found")
    
    try:
        result = db.execute("""
            INSERT INTO ticker_prices (price_id, ticker_id, date, price, created_at, updated_at)
            VALUES (nextval('seq_ticker_prices'), ?, ?, ?, ?, ?)
            RETURNING *
        """, [price.ticker_id, price.date, price.price, now, now]).fetchone()
        
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Price already exists for this ticker on {price.date}"
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{price_id}", response_model=TickerPrice)
def update_ticker_price(
    price_id: int,
    price: TickerPriceUpdate,
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update a ticker price"""
    # Check if price exists
    existing = db.execute(
        "SELECT * FROM ticker_prices WHERE price_id = ?", [price_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Ticker price not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if price.ticker_id is not None:
        update_fields.append("ticker_id = ?")
        params.append(price.ticker_id)
    
    if price.date is not None:
        update_fields.append("date = ?")
        params.append(price.date)
    
    if price.price is not None:
        update_fields.append("price = ?")
        params.append(price.price)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(price_id)
    
    query = f"UPDATE ticker_prices SET {', '.join(update_fields)} WHERE price_id = ? RETURNING *"
    
    try:
        result = db.execute(query, params).fetchone()
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Price already exists for this ticker on this date"
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{price_id}", status_code=204)
def delete_ticker_price(price_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete a ticker price"""
    result = db.execute(
        "DELETE FROM ticker_prices WHERE price_id = ? RETURNING price_id", [price_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticker price not found")
    
    return None
