#!/bin/bash

# Idea Factory - Start Script
# This script sets up and runs the Idea Factory Flask application

set -e  # Exit on error

echo "🚀 Starting Idea Factory..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your credentials:"
    echo "   cp .env.example .env"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if Google Sheets credentials are configured
if [ -f .env ]; then
    if ! grep -q "GOOGLE_SHEETS_CREDS" .env || grep -q "your_spreadsheet_id_here" .env; then
        echo "⚠️  Warning: Google Sheets credentials may not be configured properly"
        echo "   Please check your .env file"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Starting Flask application on http://localhost:5001"
echo "   Press Ctrl+C to stop"
echo ""

# Run the Flask application
python app.py
