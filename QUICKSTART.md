# Investment Tracker - Quick Reference

## 🚀 Starting the Application

### Start Everything (Recommended)
```bash
./setup.sh
```
- Installs dependencies automatically
- Starts both backend and frontend
- Press Ctrl+C to stop

### Start Individual Servers
```bash
./start-backend.sh    # Backend only
./start-frontend.sh   # Frontend only
```

## 🔗 Access URLs

| Service | URL |
|---------|-----|
| **Frontend App** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |

## 📊 API Endpoints

All endpoints prefixed with `/api`

### Resources (All support CRUD)
- `/api/accounts` - Investment accounts
- `/api/tickers` - Stock ticker prices
- `/api/holdings` - Account holdings
- `/api/properties` - Real estate properties
- `/api/property-values` - Property valuations
- `/api/property-mortgages` - Property mortgages

### Utilities
- `POST /api/backup/backup` - Backup database to JSON
- `POST /api/backup/restore` - Restore from JSON
- `GET /health` - Health check

## 📝 Common Operations

### Create an Account
```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{"account_name": "My Account", "description": "Investment account"}'
```

### Get All Accounts
```bash
curl http://localhost:8000/api/accounts
```

### Backup Database
```bash
curl -X POST http://localhost:8000/api/backup/backup
```

### Restore Database
```bash
curl -X POST http://localhost:8000/api/backup/restore
```

## 📂 File Locations

| Item | Location |
|------|----------|
| **DuckDB Database** | `backend/data/investments.db` |
| **JSON Backups** | `data/*.json` |
| **Backend Logs** | `backend.log` (when using setup.sh) |
| **Frontend Logs** | `frontend.log` (when using setup.sh) |
| **Backend Code** | `backend/app/` |
| **Frontend Code** | `frontend/src/` |

## 🛠️ Development Commands

### Backend
```bash
cd backend
source venv/bin/activate
python3 -m app.main              # Start server
pip install -r requirements.txt # Install deps
```

### Frontend
```bash
cd frontend
npm start                       # Start dev server
npm install                     # Install deps
npm run build                   # Build for production
npm test                        # Run tests
```

## 🔍 Troubleshooting

### Backend won't start
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
Backend (8000):
```bash
lsof -ti:8000 | xargs kill -9
```

Frontend (3000):
```bash
lsof -ti:3000 | xargs kill -9
```

### View logs
```bash
tail -f backend.log    # Backend logs
tail -f frontend.log   # Frontend logs
```

## 📚 Data Models

### Account
- account_id, account_name, description

### Ticker
- ticker_id, ticker_symbol, date, price

### Account Holding
- holding_id, account_id, date, ticker_symbol, shares, value, ownership

### Property
- property_id, name

### Property Value
- property_value_id, property_id, date, valuation

### Property Mortgage
- property_mortgage_id, property_id, date, mortgage

## 🎯 Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Test Endpoints**: Use the interactive API docs
3. **Build Frontend**: Add components in `frontend/src/components/`
4. **Add Analytics**: Write SQL queries against DuckDB
5. **Migrate Data**: Use `/api/backup/restore` to load existing data

## 💡 Tips

- Use `/docs` for interactive API testing
- All TypeScript types are pre-defined
- DuckDB is great for analytics queries
- JSON backups make data portable
- CORS already configured for local dev
