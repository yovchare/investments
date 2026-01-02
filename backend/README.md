# Investment Tracker Backend

FastAPI backend with DuckDB embedded database for the Investment Tracker application.

## Features

- RESTful API with FastAPI
- DuckDB embedded database
- Automatic API documentation (Swagger/OpenAPI)
- JSON backup and restore
- CORS support for frontend integration
- Pydantic data validation

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` to configure:
- `DATABASE_PATH` - Path to DuckDB database file
- `BACKUP_PATH` - Path to JSON backup directory
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

## Running the Server

Development mode (with auto-reload):
```bash
python3 -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database

The application uses DuckDB, an embedded analytical database. The database file is created automatically on first run.

### Schema

The database includes the following tables:
- `accounts` - Investment accounts
- `tickers` - Stock ticker prices
- `account_holdings` - Account holdings/positions
- `properties` - Real estate properties
- `property_values` - Property valuations over time
- `property_mortgages` - Property mortgage amounts over time

### Backup & Restore

Backup database to JSON:
```bash
curl -X POST http://localhost:8000/api/backup/backup
```

Restore database from JSON:
```bash
curl -X POST http://localhost:8000/api/backup/restore
```

JSON files are stored in the directory specified by `BACKUP_PATH` (default: `../data`).

## Project Structure

```
backend/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py     # Database connection and schema
│   │   └── backup.py          # Backup/restore functionality
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py         # Account models
│   │   ├── ticker.py          # Ticker models
│   │   ├── account_holding.py # Holding models
│   │   ├── property.py        # Property models
│   │   ├── property_value.py  # Property value models
│   │   └── property_mortgage.py # Property mortgage models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── accounts.py        # Account endpoints
│   │   ├── tickers.py         # Ticker endpoints
│   │   ├── holdings.py        # Holding endpoints
│   │   ├── properties.py      # Property endpoints
│   │   ├── property_values.py # Property value endpoints
│   │   ├── property_mortgages.py # Property mortgage endpoints
│   │   └── backup.py          # Backup endpoints
│   └── main.py                # FastAPI application
├── requirements.txt
├── .env.example
└── .gitignore
```

## Development

### Adding a New Endpoint

1. Create a Pydantic model in `app/models/`
2. Create a router in `app/routers/`
3. Register the router in `app/main.py`
4. Update the database schema in `app/database/connection.py`

### Testing

You can test the API using:
- The interactive docs at `/docs`
- curl commands
- Postman or similar API clients
- The Python `requests` library

Example:
```python
import requests

# Create an account
response = requests.post(
    "http://localhost:8000/api/accounts",
    json={"account_name": "Brokerage Account", "description": "Main investment account"}
)
print(response.json())
```

## Dependencies

- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **pydantic**: Data validation using Python type hints
- **duckdb**: Embedded analytical database
- **python-multipart**: For handling file uploads
- **python-dotenv**: For loading environment variables
