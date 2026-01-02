from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.account_holding import AccountHolding, AccountHoldingCreate, AccountHoldingUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/holdings", tags=["holdings"])


@router.get("/", response_model=List[AccountHolding])
def get_holdings(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all account holdings"""
    result = db.execute("SELECT * FROM account_holdings ORDER BY account_id, date DESC").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{holding_id}", response_model=AccountHolding)
def get_holding(holding_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific holding by ID"""
    result = db.execute(
        "SELECT * FROM account_holdings WHERE holding_id = ?", [holding_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=AccountHolding, status_code=201)
def create_holding(holding: AccountHoldingCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Create a new account holding"""
    now = datetime.now()
    
    # Verify account exists
    account = db.execute(
        "SELECT account_id FROM accounts WHERE account_id = ?", [holding.account_id]
    ).fetchone()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    result = db.execute("""
        INSERT INTO account_holdings 
        (holding_id, account_id, date, ticker_symbol, number_of_shares, value, ownership, created_at, updated_at)
        VALUES (nextval('seq_holdings'), ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *
    """, [
        holding.account_id, 
        holding.date, 
        holding.ticker_symbol, 
        holding.number_of_shares,
        holding.value,
        holding.ownership.value,
        now, 
        now
    ]).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.put("/{holding_id}", response_model=AccountHolding)
def update_holding(
    holding_id: int, 
    holding: AccountHoldingUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing account holding"""
    # Check if holding exists
    existing = db.execute(
        "SELECT * FROM account_holdings WHERE holding_id = ?", [holding_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if holding.account_id is not None:
        # Verify account exists
        account = db.execute(
            "SELECT account_id FROM accounts WHERE account_id = ?", [holding.account_id]
        ).fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        update_fields.append("account_id = ?")
        params.append(holding.account_id)
    
    if holding.date is not None:
        update_fields.append("date = ?")
        params.append(holding.date)
    
    if holding.ticker_symbol is not None:
        update_fields.append("ticker_symbol = ?")
        params.append(holding.ticker_symbol)
    
    if holding.number_of_shares is not None:
        update_fields.append("number_of_shares = ?")
        params.append(holding.number_of_shares)
    
    if holding.value is not None:
        update_fields.append("value = ?")
        params.append(holding.value)
    
    if holding.ownership is not None:
        update_fields.append("ownership = ?")
        params.append(holding.ownership.value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(holding_id)
    
    query = f"UPDATE account_holdings SET {', '.join(update_fields)} WHERE holding_id = ? RETURNING *"
    result = db.execute(query, params).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.delete("/{holding_id}", status_code=204)
def delete_holding(holding_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete an account holding"""
    result = db.execute(
        "DELETE FROM account_holdings WHERE holding_id = ? RETURNING holding_id", [holding_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    return None
