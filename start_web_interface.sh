#!/bin/bash
# Startup script for Ovi Web Interface

set -e

echo "================================================"
echo "  Ovi Web Interface Startup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ Python and Node.js found${NC}"
echo ""

# Check if API dependencies are installed
echo "Checking API dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing API dependencies...${NC}"
    pip install -r requirements_api.txt
fi
echo -e "${GREEN}✓ API dependencies ready${NC}"
echo ""

# Check if frontend dependencies are installed
echo "Checking frontend dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi
echo -e "${GREEN}✓ Frontend dependencies ready${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $API_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API server
echo "Starting API server..."
python3 api_server.py &
API_PID=$!
echo -e "${GREEN}✓ API server started (PID: $API_PID)${NC}"
echo "   API URL: http://localhost:8000"
echo ""

# Wait for API to be ready
echo "Waiting for API server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API server is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: API server failed to start${NC}"
        kill $API_PID
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   Frontend URL: http://localhost:3000"
echo ""

echo "================================================"
echo -e "${GREEN}  Ovi Web Interface is running!${NC}"
echo "================================================"
echo ""
echo "Access the interface at:"
echo "  → http://localhost:3000"
echo ""
echo "API documentation:"
echo "  → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $API_PID $FRONTEND_PID
