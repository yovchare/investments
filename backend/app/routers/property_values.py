from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.property_value import PropertyValue, PropertyValueCreate, PropertyValueUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/property-values", tags=["property-values"])


@router.get("/", response_model=List[PropertyValue])
def get_property_values(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all property values"""
    result = db.execute("SELECT * FROM property_values ORDER BY property_id, date DESC").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{property_value_id}", response_model=PropertyValue)
def get_property_value(property_value_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific property value by ID"""
    result = db.execute(
        "SELECT * FROM property_values WHERE property_value_id = ?", [property_value_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property value not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=PropertyValue, status_code=201)
def create_property_value(
    property_value: PropertyValueCreate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Create a new property value"""
    now = datetime.now()
    
    # Verify property exists
    property_exists = db.execute(
        "SELECT property_id FROM properties WHERE property_id = ?", [property_value.property_id]
    ).fetchone()
    
    if not property_exists:
        raise HTTPException(status_code=404, detail="Property not found")
    
    try:
        result = db.execute("""
            INSERT INTO property_values 
            (property_value_id, property_id, date, valuation, created_at, updated_at)
            VALUES (nextval('seq_property_values'), ?, ?, ?, ?, ?)
            RETURNING *
        """, [property_value.property_id, property_value.date, property_value.valuation, now, now]).fetchone()
        
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail="Property value already exists for this date")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{property_value_id}", response_model=PropertyValue)
def update_property_value(
    property_value_id: int, 
    property_value: PropertyValueUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing property value"""
    # Check if property value exists
    existing = db.execute(
        "SELECT * FROM property_values WHERE property_value_id = ?", [property_value_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Property value not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if property_value.property_id is not None:
        # Verify property exists
        property_exists = db.execute(
            "SELECT property_id FROM properties WHERE property_id = ?", [property_value.property_id]
        ).fetchone()
        if not property_exists:
            raise HTTPException(status_code=404, detail="Property not found")
        update_fields.append("property_id = ?")
        params.append(property_value.property_id)
    
    if property_value.date is not None:
        update_fields.append("date = ?")
        params.append(property_value.date)
    
    if property_value.valuation is not None:
        update_fields.append("valuation = ?")
        params.append(property_value.valuation)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_fields.append("updated_at = ?")
    params.append(datetime.now())
    params.append(property_value_id)
    
    query = f"UPDATE property_values SET {', '.join(update_fields)} WHERE property_value_id = ? RETURNING *"
    
    try:
        result = db.execute(query, params).fetchone()
        columns = [desc[0] for desc in db.description]
        return dict(zip(columns, result))
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=400, detail="Property value already exists for this date")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{property_value_id}", status_code=204)
def delete_property_value(property_value_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete a property value"""
    result = db.execute(
        "DELETE FROM property_values WHERE property_value_id = ? RETURNING property_value_id", 
        [property_value_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property value not found")
    
    return None
