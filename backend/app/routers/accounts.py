from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.account import Account, AccountCreate, AccountUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[Account])
def get_accounts(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all accounts"""
    result = db.execute("SELECT * FROM accounts ORDER BY account_id").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific account by ID"""
    result = db.execute(
        "SELECT * FROM accounts WHERE account_id = ?", [account_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=Account, status_code=201)
def create_account(account: AccountCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Create a new account"""
    now = datetime.now()
    
    result = db.execute("""
        INSERT INTO accounts (account_id, account_name, description, created_at, updated_at)
        VALUES (nextval('seq_accounts'), ?, ?, ?, ?)
        RETURNING *
    """, [account.account_name, account.description, now, now]).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.put("/{account_id}", response_model=Account)
def update_account(
    account_id: int, 
    account: AccountUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing account"""
    # Check if account exists
    existing = db.execute(
        "SELECT * FROM accounts WHERE account_id = ?", [account_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if account.account_name is not None:
        update_fields.append("account_name = ?")
        params.append(account.account_name)
    
    if account.description is not None:
        update_fields.append("description = ?")
        params.append(account.description)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(account_id)
    
    query = f"UPDATE accounts SET {', '.join(update_fields)} WHERE account_id = ? RETURNING *"
    result = db.execute(query, params).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete an account"""
    result = db.execute(
        "DELETE FROM accounts WHERE account_id = ? RETURNING account_id", [account_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return None
