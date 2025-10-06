#!/bin/bash

# =============================================================================
# Project IRIS - Environment Setup Script
# =============================================================================

echo "🐍 Project IRIS - Environment Setup"
echo "==================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📋 Current Python version: $(python3 --version)"

if (( $(echo "$python_version >= 3.11" | bc -l) )); then
    echo "✅ Python version is compatible"
else
    echo "⚠️  Python version might be too old. Recommend Python 3.11+"
fi

echo ""
echo "📦 Installing dependencies..."

# Try to install with current Python
if pip3 install -r requirements.txt; then
    echo "✅ Dependencies installed successfully!"
else
    echo ""
    echo "❌ Installation failed. This might be due to Python version compatibility."
    echo ""
    echo "🔧 Alternative solutions:"
    echo ""
    echo "Option 1: Use Python 3.11 virtual environment (Recommended)"
    echo "python3.11 -m venv venv311"
    echo "source venv311/bin/activate"
    echo "pip install -r requirements.txt"
    echo ""
    echo "Option 2: Use conda environment with Python 3.11"
    echo "conda create -n iris python=3.11"
    echo "conda activate iris"
    echo "pip install -r requirements.txt"
    echo ""
    echo "Option 3: Use Docker (most reliable)"
    echo "docker-compose up -d"
    echo ""
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and add your API keys"
echo "2. Run: python -m pytest tests/ --version (to verify setup)"
echo "3. Run: uvicorn src.api.main:app --reload (to start development server)"
echo ""
echo "For production deployment:"
echo "docker-compose up -d"
