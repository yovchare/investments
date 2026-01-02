from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.ticker import Ticker, TickerCreate, TickerUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/tickers", tags=["tickers"])


@router.get("/", response_model=List[Ticker])
def get_tickers(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all ticker symbols"""
    result = db.execute("SELECT * FROM tickers ORDER BY ticker_symbol").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{ticker_id}", response_model=Ticker)
def get_ticker(ticker_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific ticker symbol by ID"""
    result = db.execute(
        "SELECT * FROM tickers WHERE ticker_id = ?", [ticker_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticker not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=Ticker, status_code=201)
def create_ticker(ticker: TickerCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Create a new ticker symbol"""
    now = datetime.now()
    
    try:
        result = db.execute("""
            INSERT INTO tickers (ticker_id, ticker_symbol, created_at, updated_at)
            VALUES (nextval('seq_tickers'), ?, ?, ?)
            RETURNING *
        """, [ticker.ticker_symbol, now, now]).fetchone()
        
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker.ticker_symbol} already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{ticker_id}", response_model=Ticker)
def update_ticker(
    ticker_id: int, 
    ticker: TickerUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing ticker symbol"""
    # Check if ticker exists
    existing = db.execute(
        "SELECT * FROM tickers WHERE ticker_id = ?", [ticker_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Ticker not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if ticker.ticker_symbol is not None:
        update_fields.append("ticker_symbol = ?")
        params.append(ticker.ticker_symbol)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(ticker_id)
    
    query = f"UPDATE tickers SET {', '.join(update_fields)} WHERE ticker_id = ? RETURNING *"
    
    try:
        result = db.execute(query, params).fetchone()
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail=f"Ticker {ticker.ticker_symbol} already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{ticker_id}", status_code=204)
def delete_ticker(ticker_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete a ticker"""
    result = db.execute(
        "DELETE FROM tickers WHERE ticker_id = ? RETURNING ticker_id", [ticker_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Ticker not found")
    
    return None
