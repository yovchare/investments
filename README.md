# Investment Tracker

A full-stack application for tracking financial investments and real estate across multiple accounts.

## 🚀 Quick Start

**TL;DR:** Run `./setup.sh` to install everything and start both servers!

See [QUICKSTART.md](QUICKSTART.md) for a complete quick reference guide.

## Architecture

- **Backend**: FastAPI with DuckDB embedded database
- **Frontend**: React with TypeScript
- **Database**: DuckDB (embedded analytical database)
- **Data Backup**: JSON files for easy restore

## Project Structure

```
investments/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── database/     # Database connection and backup utilities
│   │   ├── models/       # Pydantic models
│   │   ├── routers/      # API endpoints
│   │   └── main.py       # FastAPI application
│   ├── requirements.txt
│   └── .env.example
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API client services
│   │   └── types/        # TypeScript type definitions
│   ├── package.json
│   └── .env.example
├── data/                 # JSON backup files
└── README.md
```

## Data Models

### Core Entities

1. **Account**: Investment accounts (Account ID, Name, Description)
2. **Ticker**: Stock prices (Ticker Symbol, Date, Price)
3. **Account Holding**: Holdings per account (Account ID, Date, Ticker, Shares, Value, Ownership Status)
4. **Property**: Real estate properties (Property ID, Name)
5. **Property Value**: Property valuations over time (Property ID, Date, Valuation)
6. **Property Mortgage**: Mortgage amounts over time (Property ID, Date, Mortgage)

## Quick Start

### Option 1: Automated Setup (Recommended)

Start both backend and frontend with automatic dependency installation:

```bash
./setup.sh
```

This will:
- ✅ Install backend dependencies (if needed)
- ✅ Install frontend dependencies (if needed)
- ✅ Start the backend server at http://localhost:8000
- ✅ Start the frontend server at http://localhost:3000
- ✅ Display access URLs and logs

Press `Ctrl+C` to stop both servers.

### Option 2: Start Servers Individually

Start just the backend:
```bash
./start-backend.sh
```

Start just the frontend:
```bash
./start-frontend.sh
```

### Option 3: Manual Setup

**Backend Setup:**

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
python3 -m app.main
```

The backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

**Frontend Setup:**

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

All endpoints are prefixed with `/api`

### Accounts
- `GET /api/accounts` - List all accounts
- `GET /api/accounts/{id}` - Get account by ID
- `POST /api/accounts` - Create new account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account

### Tickers
- `GET /api/tickers` - List all tickers
- `GET /api/tickers/{id}` - Get ticker by ID
- `POST /api/tickers` - Create new ticker
- `PUT /api/tickers/{id}` - Update ticker
- `DELETE /api/tickers/{id}` - Delete ticker

### Holdings
- `GET /api/holdings` - List all holdings
- `GET /api/holdings/{id}` - Get holding by ID
- `POST /api/holdings` - Create new holding
- `PUT /api/holdings/{id}` - Update holding
- `DELETE /api/holdings/{id}` - Delete holding

### Properties
- `GET /api/properties` - List all properties
- `GET /api/properties/{id}` - Get property by ID
- `POST /api/properties` - Create new property
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property

### Property Values
- `GET /api/property-values` - List all property values
- `GET /api/property-values/{id}` - Get property value by ID
- `POST /api/property-values` - Create new property value
- `PUT /api/property-values/{id}` - Update property value
- `DELETE /api/property-values/{id}` - Delete property value

### Property Mortgages
- `GET /api/property-mortgages` - List all property mortgages
- `GET /api/property-mortgages/{id}` - Get property mortgage by ID
- `POST /api/property-mortgages` - Create new property mortgage
- `PUT /api/property-mortgages/{id}` - Update property mortgage
- `DELETE /api/property-mortgages/{id}` - Delete property mortgage

### Backup & Restore
- `POST /api/backup/backup` - Backup database to JSON files
- `POST /api/backup/restore` - Restore database from JSON files

## Database

The application uses DuckDB, an embedded analytical database that runs within the Python process. This provides:

- Zero configuration - no separate database server needed
- Excellent analytical query performance
- ACID compliance
- SQL interface

Data is automatically backed up to JSON files in the `data/` directory for easy restore and portability.

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation. Visit `/docs` for interactive API exploration.

Key files:
- `app/main.py` - Application entry point
- `app/database/connection.py` - Database setup and connection
- `app/models/` - Pydantic models for data validation
- `app/routers/` - API endpoint definitions

### Frontend Development

The frontend is built with React and TypeScript, providing type safety throughout the application.

Key files:
- `src/App.tsx` - Main application component
- `src/services/` - API client services
- `src/types/` - TypeScript type definitions
- `src/components/` - React components

## Features

- ✅ Complete CRUD operations for all entities
- ✅ Type-safe API with Pydantic validation
- ✅ Embedded DuckDB database
- ✅ JSON backup and restore functionality
- ✅ CORS-enabled API
- ✅ Interactive API documentation
- ✅ TypeScript frontend for type safety
- 🚧 Advanced analytics (coming soon)
- 🚧 Data visualization (coming soon)
- 🚧 User authentication (coming soon)

## License

MIT
