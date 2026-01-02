#!/bin/bash

echo "🚀 Starting Investment Tracker Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not found. Run setup.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
fi

echo "Starting React development server..."
echo "App will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm start
