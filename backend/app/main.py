from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database.connection import db
from app.routers import (
    accounts,
    tickers,
    ticker_prices,
    holdings,
    properties,
    property_values,
    property_mortgages,
    backup
)

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup: Connect to database
    db.connect()
    print("Database connected")
    yield
    # Shutdown: Close database connection
    db.close()
    print("Database connection closed")


app = FastAPI(
    title="Investment Tracker API",
    description="API for tracking financial investments and real estate",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(accounts.router, prefix="/api")
app.include_router(tickers.router, prefix="/api")
app.include_router(ticker_prices.router, prefix="/api")
app.include_router(holdings.router, prefix="/api")
app.include_router(properties.router, prefix="/api")
app.include_router(property_values.router, prefix="/api")
app.include_router(property_mortgages.router, prefix="/api")
app.include_router(backup.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Investment Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
