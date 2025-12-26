#!/bin/bash

# Network Diagnostics Tool - Quick Setup Script
# For Linux and macOS

echo "=========================================="
echo "Network Diagnostics Tool - Quick Setup"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env configuration file..."
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo ""
    echo "⚠️  NOTE: Please review and customize .env file for your environment"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs bulk_results
echo "✅ Directories created"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "  1. Activate the virtual environment (if not already active):"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python app.py"
echo ""
echo "  3. Open your browser to:"
echo "     http://localhost:8080"
echo ""
echo "To customize settings, edit the .env file"
echo ""
echo "For more information, see README.md"
echo "=========================================="
