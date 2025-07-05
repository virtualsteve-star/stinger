#!/bin/bash

echo "🚀 Starting Stinger Management Console..."

# Kill any existing processes
pkill -f "python.*main.py.*8001" 2>/dev/null

# Start backend
echo "Starting backend on port 8001..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Test backend
echo "Testing backend..."
curl -s http://localhost:8001/api/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend is running on http://localhost:8001"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting frontend..."
cd frontend
npm install --silent
npm start

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT