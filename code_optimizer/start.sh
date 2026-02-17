#!/bin/bash

# Code Optimizer - Quick Start Script
# Starts both backend server and frontend

echo "🚀 Starting Code Optimizer..."
echo ""

# Check if backend is already running
echo "Checking if backend is already running..."
if lsof -i :5001 > /dev/null 2>&1; then
    echo "✓ Backend is already running on port 5001"
else
    echo "Starting backend server on port 5001..."
    cd "$(dirname "$0")/backend"
    python3 app.py &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
    sleep 2
fi

echo ""
echo "==========================================="
echo "📊 Code Optimizer is Ready!"
echo "==========================================="
echo ""
echo "Backend API:    http://localhost:5001"
echo "Frontend File:  frontend/index.html"
echo ""
echo "To access the web interface:"
echo "  1. Open frontend/index.html in your browser"
echo "  2. Or use a local server:"
echo "     cd frontend"
echo "     python3 -m http.server 8000"
echo "     Then visit http://localhost:8000"
echo ""
echo "To test the API:"
echo "  curl http://localhost:5001/health"
echo ""
echo "Press Ctrl+C to stop the backend server"
echo "==========================================="
echo ""

# Keep script running
wait
