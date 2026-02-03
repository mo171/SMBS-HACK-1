#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting SMBS-HACK-1 Application..."

# Start backend in background
echo "📦 Starting FastAPI Backend on port 8000..."
cd /app/backend/app
uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start frontend in foreground
echo "🌐 Starting Next.js Frontend on port 3000..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Function to handle shutdown
shutdown() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID
    wait $BACKEND_PID $FRONTEND_PID
    echo "✅ Services stopped"
    exit 0
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
