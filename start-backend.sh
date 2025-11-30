#!/bin/bash

# Start the Python backend server

echo "Starting Timestable Tutor Backend..."
echo ""

# Check if .env exists and has API key
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your Google API key."
    echo "See .env.template for an example."
    exit 1
fi

# Check if API key is set
if ! grep -q "GOOGLE_API_KEY=.\+" .env; then
    echo "ERROR: GOOGLE_API_KEY not set in .env file!"
    echo "Please add your Google API key to the .env file."
    echo "Get your key from: https://aistudio.google.com/apikey"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Create data directory if it doesn't exist
mkdir -p data

# Start the server
echo ""
echo "========================================"
echo "Backend server starting on port 8000"
echo "========================================"
echo ""
python main.py
