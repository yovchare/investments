# Investment Tracker - Project Overview

## 🎯 Project Summary

Full-stack financial tracking application with FastAPI backend and React frontend, using DuckDB as an embedded analytical database.

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    React + TypeScript                        │
│                   http://localhost:3000                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │  Components  │  │   Services   │     │
│  │              │  │              │  │  (API Client)│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                          │ HTTP/REST API
                          │
┌──────────────────────────▼──────────────────────────────────┐
│                         Backend                              │
│                  FastAPI + Python                            │
│                   http://localhost:8000                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routers    │  │   Models     │  │   Database   │     │
│  │  (Endpoints) │  │  (Pydantic)  │  │  (DuckDB)    │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
└─────────────────────────────────────────────┼──────────────┘
                                              │
                          ┌───────────────────▼────────────────┐
                          │    DuckDB Database                 │
                          │    ./data/investments.db           │
                          │                                    │
                          │  ┌──────────────────────────────┐ │
                          │  │ Backup/Restore to JSON Files │ │
                          │  │    ../data/*.json            │ │
                          │  └──────────────────────────────┘ │
                          └────────────────────────────────────┘
```

## 📁 Complete Project Structure

```
investments/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app + CORS config
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # DuckDB connection + schema
│   │   │   └── backup.py             # JSON backup/restore
│   │   │
│   │   ├── models/                   # Pydantic Models
│   │   │   ├── __init__.py
│   │   │   ├── account.py            # Account models
│   │   │   ├── ticker.py             # Ticker models
│   │   │   ├── account_holding.py    # Holding models
│   │   │   ├── property.py           # Property models
│   │   │   ├── property_value.py     # Property value models
│   │   │   └── property_mortgage.py  # Property mortgage models
│   │   │
│   │   └── routers/                  # API Endpoints (CRUD)
│   │       ├── __init__.py
│   │       ├── accounts.py           # Account endpoints
│   │       ├── tickers.py            # Ticker endpoints
│   │       ├── holdings.py           # Holding endpoints
│   │       ├── properties.py         # Property endpoints
│   │       ├── property_values.py    # Property value endpoints
│   │       ├── property_mortgages.py # Property mortgage endpoints
│   │       └── backup.py             # Backup/restore endpoints
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   ├── .gitignore
│   └── README.md
│
├── frontend/                         # React Frontend
│   ├── public/
│   │   └── index.html                # HTML template
│   │
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.tsx         # Main dashboard
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                # Axios client config
│   │   │   └── index.ts              # API service functions
│   │   │
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript type definitions
│   │   │
│   │   ├── App.tsx                   # Main app component
│   │   ├── App.css                   # App styles
│   │   ├── index.tsx                 # React entry point
│   │   └── index.css                 # Global styles
│   │
│   ├── package.json                  # NPM dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── .env.example                  # Environment variables template
│   ├── .gitignore
│   └── README.md
│
├── data/                             # JSON Backup Files
│   ├── accounts.json                 # (existing)
│   ├── tickers.json                  # (existing)
│   ├── account_balances.json         # (existing)
│   ├── daily_balances.json           # (existing)
│   ├── mortgage.json                 # (existing)
│   ├── property_value.json           # (existing)
│   └── unvested_balances.json        # (existing)
│
├── scripts/                          # Utility Scripts
│   ├── calculate_daily_balances.py   # (existing)
│   └── fetch_ticker_data.py          # (existing)
│
├── README.md                         # Main documentation
├── setup.sh                          # Quick setup script
└── OVERVIEW.md                       # This file
```

## 🗄️ Database Schema

### Tables

**accounts**
- account_id (PK)
- account_name
- description
- created_at
- updated_at

**tickers**
- ticker_id (PK)
- ticker_symbol
- date
- price
- created_at
- updated_at
- UNIQUE(ticker_symbol, date)

**account_holdings**
- holding_id (PK)
- account_id (FK)
- date
- ticker_symbol
- number_of_shares
- value
- ownership (Owned/Unowned/Unvested)
- created_at
- updated_at

**properties**
- property_id (PK)
- name
- created_at
- updated_at

**property_values**
- property_value_id (PK)
- property_id (FK)
- date
- valuation
- created_at
- updated_at
- UNIQUE(property_id, date)

**property_mortgages**
- property_mortgage_id (PK)
- property_id (FK)
- date
- mortgage
- created_at
- updated_at
- UNIQUE(property_id, date)

## 🚀 Getting Started

### Option 1: Automated Start (Recommended)
```bash
./setup.sh
```
This single command will:
- Install all dependencies (backend + frontend)
- Start both servers automatically
- Show you all access URLs and logs
- Run until you press Ctrl+C

### Option 2: Individual Server Scripts
```bash
./start-backend.sh   # Just the backend
./start-frontend.sh  # Just the frontend
```

### Option 3: Manual setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python3 -m app.main
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

## 📝 Startup Scripts

- **setup.sh** - Complete setup and start both servers
- **start-backend.sh** - Start only the backend server
- **start-frontend.sh** - Start only the frontend server

All scripts handle dependency installation automatically.

## 🔗 API Endpoints

### Core Resources
- `/api/accounts` - Account management
- `/api/tickers` - Stock ticker prices
- `/api/holdings` - Account holdings/positions
- `/api/properties` - Real estate properties
- `/api/property-values` - Property valuations
- `/api/property-mortgages` - Property mortgages

### Utilities
- `/api/backup/backup` - Backup to JSON
- `/api/backup/restore` - Restore from JSON
- `/docs` - Interactive API docs (Swagger)
- `/redoc` - Alternative API docs

### CRUD Operations
Each resource supports:
- `GET /resource` - List all
- `GET /resource/{id}` - Get one
- `POST /resource` - Create
- `PUT /resource/{id}` - Update
- `DELETE /resource/{id}` - Delete

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **DuckDB** - Embedded analytical database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Python-dotenv** - Environment management

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Axios** - HTTP client
- **Create React App** - Tooling

### Database
- **DuckDB** - Embedded SQL database
  - Zero configuration
  - Analytical query performance
  - ACID compliant
  - JSON backup/restore

## 📝 Key Features Implemented

✅ **Backend**
- Complete CRUD APIs for all entities
- DuckDB database with auto-initialization
- JSON backup and restore functionality
- Input validation with Pydantic
- CORS configuration for frontend
- Interactive API documentation
- Foreign key constraints
- Unique constraints on key fields

✅ **Frontend**
- TypeScript for type safety
- API service layer
- Type definitions matching backend
- Basic dashboard UI
- Axios client configuration
- Environment variable support

## 🔮 Future Enhancements

**Analytics & Visualization**
- Portfolio performance over time
- Asset allocation charts
- Net worth calculations
- Return on investment metrics

**User Interface**
- Data tables with sorting/filtering
- Forms for CRUD operations
- Charts and graphs
- Responsive design improvements

**Features**
- User authentication
- Data import/export
- Automated ticker price fetching
- Email notifications
- Mobile app

## 📚 Documentation

- Main README: `/README.md`
- Backend docs: `/backend/README.md`
- Frontend docs: `/frontend/README.md`
- API docs: `http://localhost:8000/docs` (when running)

## 🤝 Development Workflow

1. Start backend: `cd backend && python -m app.main`
2. Start frontend: `cd frontend && npm start`
3. Access API docs: http://localhost:8000/docs
4. Access app: http://localhost:3000
5. Make changes and test
6. Backup data: `POST /api/backup/backup`

## 🔒 Security Notes

- No authentication implemented yet
- Database is local file
- CORS allows localhost:3000 and localhost:5173
- Environment variables in .env files
- .env files are gitignored

## 💡 Tips

- Use `/docs` for testing API endpoints interactively
- Backup data regularly with `/api/backup/backup`
- TypeScript types are already defined for all entities
- DuckDB file is in `backend/data/investments.db`
- JSON backups are in `data/` directory
