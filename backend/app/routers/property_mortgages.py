from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.property_mortgage import PropertyMortgage, PropertyMortgageCreate, PropertyMortgageUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/property-mortgages", tags=["property-mortgages"])


@router.get("/", response_model=List[PropertyMortgage])
def get_property_mortgages(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all property mortgages"""
    result = db.execute("SELECT * FROM property_mortgages ORDER BY property_id, date DESC").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{property_mortgage_id}", response_model=PropertyMortgage)
def get_property_mortgage(property_mortgage_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific property mortgage by ID"""
    result = db.execute(
        "SELECT * FROM property_mortgages WHERE property_mortgage_id = ?", [property_mortgage_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property mortgage not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=PropertyMortgage, status_code=201)
def create_property_mortgage(
    property_mortgage: PropertyMortgageCreate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Create a new property mortgage"""
    now = datetime.now()
    
    # Verify property exists
    property_exists = db.execute(
        "SELECT property_id FROM properties WHERE property_id = ?", [property_mortgage.property_id]
    ).fetchone()
    
    if not property_exists:
        raise HTTPException(status_code=404, detail="Property not found")
    
    try:
        result = db.execute("""
            INSERT INTO property_mortgages 
            (property_mortgage_id, property_id, date, mortgage, created_at, updated_at)
            VALUES (nextval('seq_property_mortgages'), ?, ?, ?, ?, ?)
            RETURNING *
        """, [property_mortgage.property_id, property_mortgage.date, property_mortgage.mortgage, now, now]).fetchone()
        
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail="Property mortgage already exists for this date")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{property_mortgage_id}", response_model=PropertyMortgage)
def update_property_mortgage(
    property_mortgage_id: int, 
    property_mortgage: PropertyMortgageUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing property mortgage"""
    # Check if property mortgage exists
    existing = db.execute(
        "SELECT * FROM property_mortgages WHERE property_mortgage_id = ?", [property_mortgage_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Property mortgage not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if property_mortgage.property_id is not None:
        # Verify property exists
        property_exists = db.execute(
            "SELECT property_id FROM properties WHERE property_id = ?", [property_mortgage.property_id]
        ).fetchone()
        if not property_exists:
            raise HTTPException(status_code=404, detail="Property not found")
        update_fields.append("property_id = ?")
        params.append(property_mortgage.property_id)
    
    if property_mortgage.date is not None:
        update_fields.append("date = ?")
        params.append(property_mortgage.date)
    
    if property_mortgage.mortgage is not None:
        update_fields.append("mortgage = ?")
        params.append(property_mortgage.mortgage)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(property_mortgage_id)
    
    query = f"UPDATE property_mortgages SET {', '.join(update_fields)} WHERE property_mortgage_id = ? RETURNING *"
    
    try:
        result = db.execute(query, params).fetchone()
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail="Property mortgage already exists for this date")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_mortgage_id}", status_code=204)
def delete_property_mortgage(property_mortgage_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete a property mortgage"""
    result = db.execute(
        "DELETE FROM property_mortgages WHERE property_mortgage_id = ? RETURNING property_mortgage_id", 
        [property_mortgage_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property mortgage not found")
    
    return None
