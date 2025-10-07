#!/bin/bash
# This script will help you fix the DATABASE_URL in your .env file

echo "Current DATABASE_URL (may have line breaks):"
grep "DATABASE_URL" .env

echo ""
echo "The DATABASE_URL should be on ONE line with no breaks."
echo ""
echo "Please edit your .env file and make sure this line is complete:"
echo "DATABASE_URL=postgresql://postgres.rsyyqooksgsdbnzjiusn:iris_password@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
echo ""
echo "Steps:"
echo "1. Open .env file: nano .env"
echo "2. Find the DATABASE_URL line"
echo "3. Make sure it's all on ONE line (no line breaks)"
echo "4. Save and exit (Ctrl+O, Enter, Ctrl+X)"
echo ""
echo "After fixing, run: python check_env.py"
