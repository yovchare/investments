import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import Any, Dict
import duckdb

from app.database.connection import get_db


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def backup_to_json(backup_dir: str = "../data"):
    """Backup all database tables to JSON files"""
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    db = get_db()
    tables = [
        "accounts",
        "tickers",
        "account_holdings",
        "properties",
        "property_values",
        "property_mortgages"
    ]
    
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for table in tables:
        result = db.execute(f"SELECT * FROM {table}").fetchall()
        columns = [desc[0] for desc in db.description]
        
        data = [dict(zip(columns, row)) for row in result]
        
        # Save to JSON file
        filename = f"{backup_dir}/{table}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, cls=DateTimeEncoder)
        
        print(f"Backed up {table} to {filename} ({len(data)} records)")
    
    print(f"\nBackup completed at {backup_timestamp}")
    return {"status": "success", "timestamp": backup_timestamp, "tables": tables}


def restore_from_json(backup_dir: str = "../data"):
    """Restore database from JSON files"""
    db = get_db()
    
    tables_config = [
        {"name": "accounts", "id_field": "account_id"},
        {"name": "tickers", "id_field": "ticker_id"},
        {"name": "account_holdings", "id_field": "holding_id"},
        {"name": "properties", "id_field": "property_id"},
        {"name": "property_values", "id_field": "property_value_id"},
        {"name": "property_mortgages", "id_field": "property_mortgage_id"}
    ]
    
    restored_counts = {}
    
    for table_config in tables_config:
        table = table_config["name"]
        id_field = table_config["id_field"]
        filename = f"{backup_dir}/{table}.json"
        
        if not os.path.exists(filename):
            print(f"Skipping {table}: file not found")
            continue
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if not data:
            print(f"Skipping {table}: no data")
            continue
        
        # Clear existing data
        db.execute(f"DELETE FROM {table}")
        
        # Insert data
        for record in data:
            columns = list(record.keys())
            placeholders = ', '.join(['?' for _ in columns])
            values = [record[col] for col in columns]
            
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            db.execute(query, values)
        
        # Update sequence to max ID + 1
        max_id_result = db.execute(f"SELECT MAX({id_field}) FROM {table}").fetchone()
        max_id = max_id_result[0] if max_id_result[0] is not None else 0
        
        sequence_name = f"seq_{table}" if table != "account_holdings" else "seq_holdings"
        db.execute(f"DROP SEQUENCE IF EXISTS {sequence_name}")
        db.execute(f"CREATE SEQUENCE {sequence_name} START {max_id + 1}")
        
        restored_counts[table] = len(data)
        print(f"Restored {table}: {len(data)} records")
    
    print("\nRestore completed")
    return {"status": "success", "restored": restored_counts}
