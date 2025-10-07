#!/usr/bin/env python3
"""Check environment variables"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

vars_to_check = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SUPABASE_DB_PASSWORD",
    "DATABASE_URL",
]

for var in vars_to_check:
    value = os.getenv(var)
    if value:
        if var in ["SUPABASE_KEY", "SUPABASE_DB_PASSWORD"]:
            masked = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            print(f"✓ {var}: {masked}")
        elif var == "DATABASE_URL":
            # Mask password in URL
            if ":" in value and "@" in value:
                parts = value.split(":")
                if len(parts) >= 3:
                    password_part = parts[2].split("@")[0]
                    masked_url = value.replace(password_part, "***")
                    print(f"✓ {var}: {masked_url}")
                else:
                    print(f"✓ {var}: {value}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✓ {var}: {value}")
    else:
        print(f"✗ {var}: NOT SET")

print("=" * 60)

# Check if SUPABASE_URL is correct format
supabase_url = os.getenv("SUPABASE_URL", "")
if supabase_url.startswith("postgresql://"):
    print("\n⚠️  WARNING: SUPABASE_URL should be HTTPS, not PostgreSQL!")
    print("   Change it to: https://rsyyqooksgsdbnzjiusn.supabase.co")
elif supabase_url.startswith("https://"):
    print("\n✓ SUPABASE_URL format is correct")
else:
    print("\n✗ SUPABASE_URL format is invalid")

# Check if DATABASE_URL is set
database_url = os.getenv("DATABASE_URL")
if database_url:
    print("✓ DATABASE_URL is set and will be used for database connection")
else:
    print("✗ DATABASE_URL is not set, will construct from SUPABASE_DB_PASSWORD")

print()
