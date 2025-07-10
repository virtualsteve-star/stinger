#!/bin/bash

echo "🚀 Starting Stinger Management Console..."

# Check for detached mode
DETACHED_MODE=false
if [[ "$1" == "--detached" ]] || [[ "$1" == "--background" ]]; then
    DETACHED_MODE=true
fi

# Kill any existing processes
pkill -f "python.*main.py.*8001" 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

if [ "$DETACHED_MODE" = true ]; then
    # Start in detached mode
    echo "Starting in detached mode..."
    
    # Start backend
    echo "Starting backend on port 8001..."
    cd backend
    nohup python3 main.py > /tmp/stinger_console_backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/stinger_console_backend.pid
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
        echo "Check logs at /tmp/stinger_console_backend.log"
        exit 1
    fi
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install --silent
    fi
    nohup npm start > /tmp/stinger_console_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/stinger_console_frontend.pid
    
    echo ""
    echo "✅ Management Console started successfully!"
    echo ""
    echo "📊 Access Points:"
    echo "   Frontend UI: http://localhost:3001"
    echo "   Backend API: http://localhost:8001"
    echo ""
    echo "📋 Log files:"
    echo "   Backend:  /tmp/stinger_console_backend.log"
    echo "   Frontend: /tmp/stinger_console_frontend.log"
    echo ""
    echo "💡 To stop:"
    echo "   kill \$(cat /tmp/stinger_console_backend.pid /tmp/stinger_console_frontend.pid)"
else
    # Start in interactive mode
    echo "Starting in interactive mode (use --detached for background mode)..."
    
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
fi