#!/bin/bash
# Stable demo startup script that avoids memory issues

echo "🚀 Starting Stinger Web Demo (Stable Mode)"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

# Step 1: Build frontend
echo -e "\n${YELLOW}Step 1: Building frontend...${NC}"
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi
echo -e "${GREEN}✅ Frontend built successfully${NC}"

# Step 2: Start backend
cd ../backend
echo -e "\n${YELLOW}Step 2: Starting backend server...${NC}"
python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    curl -s http://localhost:8000/api/health > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Step 3: Start frontend production server
cd ..
echo -e "\n${YELLOW}Step 3: Starting frontend server...${NC}"
node serve-production.js &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo "Waiting for frontend to be ready..."
sleep 3

echo -e "\n${GREEN}✅ Demo is running!${NC}"
echo "===================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
wait