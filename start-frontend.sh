#!/bin/bash

# Start the Next.js frontend

echo "Starting Timestable Tutor Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Node modules not found. Installing dependencies..."
    npm install
fi

# Start the development server
echo ""
echo "========================================"
echo "Frontend starting on port 3000"
echo "========================================"
echo ""
npm run dev
