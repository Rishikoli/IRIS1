#!/bin/bash

# =============================================================================
# Project IRIS - Infrastructure Verification Script
# =============================================================================

echo "🔍 Project IRIS - Infrastructure Verification"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Are you in the project root?"
    exit 1
fi

echo "✅ Project structure verified"

# Check Python version
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ Error: pip not found"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "⚠️  Warning: Docker not found. Install Docker to run full stack."
else
    echo "🐳 Docker version: $(docker --version)"
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Warning: docker-compose not found. Install docker-compose to run services."
else
    echo "🐳 docker-compose version: $(docker-compose --version)"
fi

# Verify key files exist
required_files=(
    "src/config.py"
    "src/api/main.py"
    "src/celery_app.py"
    "src/tasks.py"
    "src/database/migrations/create_tables.sql"
    "docker-compose.yml"
    "Dockerfile"
    ".env.template"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🎉 Infrastructure verification completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and add your API keys"
echo "2. Run: docker-compose up -d"
echo "3. Check: docker-compose ps"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "For development without Docker:"
echo "1. Set up PostgreSQL, Redis, and ChromaDB"
echo "2. Run: uvicorn src.api.main:app --reload"
echo "3. Run: celery -A src.celery_app worker --loglevel=info"
