import duckdb
import os
from pathlib import Path
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "./data/investments.db"):
        self.db_path = db_path
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        """Establish connection to DuckDB"""
        self.conn = duckdb.connect(self.db_path)
        self._initialize_schema()
        
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def _initialize_schema(self):
        """Create tables if they don't exist"""
        
        # Accounts table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INTEGER PRIMARY KEY,
                account_name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create sequence for accounts
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_accounts START 1
        """)
        
        # Tickers table - symbols user wants to track
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                ticker_id INTEGER PRIMARY KEY,
                ticker_symbol VARCHAR(10) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_tickers START 1
        """)
        
        # Ticker prices table - historical price data
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ticker_prices (
                price_id INTEGER PRIMARY KEY,
                ticker_id INTEGER NOT NULL,
                date DATE NOT NULL,
                price DOUBLE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id),
                UNIQUE(ticker_id, date)
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_ticker_prices START 1
        """)
        
        # Account Holdings table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS account_holdings (
                holding_id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                date DATE NOT NULL,
                ticker_symbol VARCHAR(10) NOT NULL,
                number_of_shares DOUBLE NOT NULL,
                value DOUBLE NOT NULL,
                ownership VARCHAR(20) NOT NULL CHECK (ownership IN ('Owned', 'Unowned', 'Unvested')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_holdings START 1
        """)
        
        # Properties table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                property_id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_properties START 1
        """)
        
        # Property Values table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS property_values (
                property_value_id INTEGER PRIMARY KEY,
                property_id INTEGER NOT NULL,
                date DATE NOT NULL,
                valuation DOUBLE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(property_id),
                UNIQUE(property_id, date)
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_property_values START 1
        """)
        
        # Property Mortgages table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS property_mortgages (
                property_mortgage_id INTEGER PRIMARY KEY,
                property_id INTEGER NOT NULL,
                date DATE NOT NULL,
                mortgage DOUBLE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(property_id),
                UNIQUE(property_id, date)
            )
        """)
        
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_property_mortgages START 1
        """)
        
    def get_connection(self):
        """Get the database connection"""
        if not self.conn:
            self.connect()
        return self.conn


# Global database instance
db = Database()


def get_db():
    """Dependency for FastAPI routes"""
    if not db.conn:
        db.connect()
    return db.conn
