#!/bin/bash

# Portfolio Diversification Analyzer - Startup Script

echo "🚀 Starting Portfolio Diversification Analyzer..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "💡 You can create one from .env.example or enter your API key in the app"
    echo ""
fi

# Start the Streamlit app
echo "🎉 Launching Streamlit app..."
echo ""
streamlit run app.py
