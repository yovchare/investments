from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import duckdb

from app.database.backup import backup_to_json, restore_from_json
from app.database.connection import get_db

router = APIRouter(prefix="/backup", tags=["backup"])


@router.post("/backup")
def backup_database(backup_dir: str = "../data") -> Dict[str, Any]:
    """
    Backup all database tables to JSON files
    
    - **backup_dir**: Directory where JSON backup files will be saved (default: ../data)
    """
    try:
        result = backup_to_json(backup_dir)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/restore")
def restore_database(backup_dir: str = "../data") -> Dict[str, Any]:
    """
    Restore database from JSON files
    
    - **backup_dir**: Directory containing JSON backup files (default: ../data)
    """
    try:
        result = restore_from_json(backup_dir)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
