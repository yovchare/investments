#!/bin/bash

echo "🚀 Starting Investment Tracker Backend..."
echo ""

cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate venv and start server
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
fi

echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m app.main
