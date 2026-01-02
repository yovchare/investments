#!/bin/bash

echo "==================================="
echo "Investment Tracker - Quick Start"
echo "==================================="
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    cd ..
    echo "✅ Backend setup complete"
else
    echo "✅ Backend already set up"
fi

echo ""

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    cd ..
    echo "✅ Frontend setup complete"
else
    echo "✅ Frontend already set up"
fi

echo ""
echo "==================================="
echo "Starting servers..."
echo "==================================="
echo ""

# Start backend
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
python3 -m app.main > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "   Backend running on http://localhost:8000 (PID: $BACKEND_PID)"
echo "   API docs: http://localhost:8000/docs"

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "🚀 Starting frontend server..."
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"

echo ""
echo "==================================="
echo "✅ All servers started!"
echo "==================================="
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running
wait
