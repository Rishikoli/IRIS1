#!/bin/bash
# Quick PostgreSQL Setup for I.R.I.S. News Monitoring
# Run this script with your password when prompted

echo "=========================================="
echo "PostgreSQL Setup for News Monitoring"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Create database 'iris_monitoring'"
echo "  2. Load schema (tables, views, functions)"
echo "  3. Set permissions"
echo "  4. Test connection"
echo ""
read -p "Press Enter to continue..."

# Step 1: Create database
echo ""
echo "[1/4] Creating database..."
sudo -u postgres psql -c "CREATE DATABASE iris_monitoring;" 2>&1 | grep -v "already exists" || echo "✓ Database ready"

# Step 2: Load schema
echo ""
echo "[2/4] Loading schema..."
sudo -u postgres psql -d iris_monitoring -f schema.sql

# Step 3: Grant permissions
echo ""
echo "[3/4] Setting permissions..."
sudo -u postgres psql -d iris_monitoring -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;"
sudo -u postgres psql -d iris_monitoring -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;"

# Step 4: Verify tables
echo ""
echo "[4/4] Verifying setup..."
sudo -u postgres psql -d iris_monitoring -c "\dt"

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Set environment variable:"
echo "export DATABASE_URL='postgresql://postgres@localhost:5432/iris_monitoring'"
echo ""
echo "Add to ~/.bashrc to make permanent:"
echo "echo \"export DATABASE_URL='postgresql://postgres@localhost:5432/iris_monitoring'\" >> ~/.bashrc"
echo ""
echo "Test the system:"
echo "  cd /home/aditya/IRIS1/backend/src/monitoring"
echo "  python3 database.py"
echo "  python3 news_monitor.py"
echo ""
