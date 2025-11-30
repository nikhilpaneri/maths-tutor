#!/bin/bash

# Timestable Tutor - Test Runner Script
# This script runs the full test suite with coverage reporting

echo "========================================"
echo "Timestable Tutor - Running Tests"
echo "========================================"
echo ""

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please create the virtual environment first:"
    echo "  cd backend && python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov pytest-mock
fi

# Run tests
echo ""
echo "Running tests..."
echo "========================================"
echo ""

# Run pytest with coverage
pytest

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ All tests passed!"
    echo "========================================"
    echo ""
    echo "Coverage report generated:"
    echo "  - Terminal: See above"
    echo "  - HTML: backend/htmlcov/index.html"
    echo ""
    echo "To view HTML coverage report:"
    echo "  open backend/htmlcov/index.html"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ Some tests failed!"
    echo "========================================"
    echo ""
    exit 1
fi
