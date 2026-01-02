from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import duckdb

from app.models.property import Property, PropertyCreate, PropertyUpdate
from app.database.connection import get_db

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("/", response_model=List[Property])
def get_properties(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get all properties"""
    result = db.execute("SELECT * FROM properties ORDER BY property_id").fetchall()
    columns = [desc[0] for desc in db.description]
    return [dict(zip(columns, row)) for row in result]


@router.get("/{property_id}", response_model=Property)
def get_property(property_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Get a specific property by ID"""
    result = db.execute(
        "SELECT * FROM properties WHERE property_id = ?", [property_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.post("/", response_model=Property, status_code=201)
def create_property(property: PropertyCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Create a new property"""
    now = datetime.now()
    
    result = db.execute("""
        INSERT INTO properties (property_id, name, created_at, updated_at)
        VALUES (nextval('seq_properties'), ?, ?, ?)
        RETURNING *
    """, [property.name, now, now]).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.put("/{property_id}", response_model=Property)
def update_property(
    property_id: int, 
    property: PropertyUpdate, 
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Update an existing property"""
    # Check if property exists
    existing = db.execute(
        "SELECT * FROM properties WHERE property_id = ?", [property_id]
    ).fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if property.name is None:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = db.execute("""
        UPDATE properties 
        SET name = ?, updated_at = ?
        WHERE property_id = ?
        RETURNING *
    """, [property.name, datetime.now(), property_id]).fetchone()
    
    columns = [desc[0] for desc in db.description]
    return dict(zip(columns, result))


@router.delete("/{property_id}", status_code=204)
def delete_property(property_id: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """Delete a property"""
    result = db.execute(
        "DELETE FROM properties WHERE property_id = ? RETURNING property_id", [property_id]
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return None
