#!/usr/bin/env python3
"""Test database connection directly"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the database URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ DATABASE_URL not found in environment")
    sys.exit(1)

# Mask password for display
masked_url = database_url.replace("iris_password", "***") if "iris_password" in database_url else database_url

print("🔍 Testing database connection...")
print(f"📍 Database URL: {masked_url}")

try:
    import psycopg2

    # Parse connection parameters
    # Format: postgresql://user:password@host:port/database
    conn_string = database_url.replace("postgresql://", "")

    # Split user:password and host:port/database
    user_pass, host_db = conn_string.split("@")
    user, password = user_pass.split(":")
    host_port, database = host_db.split("/")
    host, port = host_port.split(":")

    print(f"👤 User: {user}")
    print(f"🌐 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🗃️  Database: {database}")

    # Test connection
    print("🔌 Attempting connection...")
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=int(port),
        database=database,
        connect_timeout=10
    )

    # Test a simple query
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

    print("✅ Connection successful!")
    print(f"✅ Test query result: {result}")

    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔧 Possible solutions:")
    print("1. Check if your password is correct")
    print("2. Verify the host and port are correct")
    print("3. Make sure the database exists and is accessible")
    print("4. Try using port 5432 instead of 6543")
    print("5. Check if you need to use a different connection format")

    if "Tenant or user not found" in str(e):
        print("\n🚨 The 'Tenant or user not found' error usually means:")
        print("   - Wrong username/password")
        print("   - Wrong host/port")
        print("   - Database doesn't exist")
        print("   - Connection string format is incorrect")

    sys.exit(1)
