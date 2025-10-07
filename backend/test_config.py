#!/usr/bin/env python3
"""Test configuration loading"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from config import settings
    
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    
    print(f"\n✓ Environment: {settings.environment}")
    print(f"✓ Supabase URL: {settings.supabase_url}")
    print(f"✓ Supabase Key: {'*' * 10}...{settings.supabase_key[-4:] if len(settings.supabase_key) > 4 else '***'}")
    print(f"✓ DB Password Set: {'Yes' if settings.supabase_db_password else 'NO - MISSING!'}")
    
    if settings.supabase_db_password:
        print(f"✓ DB Password Length: {len(settings.supabase_db_password)} characters")
        try:
            db_url = settings.database_url
            # Mask password
            masked_url = db_url.replace(settings.supabase_db_password, "***")
            print(f"\n✓ Database URL: {masked_url}")
            print(f"✓ URL Length: {len(db_url)} characters")
        except Exception as e:
            print(f"\n✗ Error constructing database URL: {e}")
    else:
        print("\n✗ SUPABASE_DB_PASSWORD is not set in .env file!")
        print("\nPlease add the following to your .env file:")
        print("SUPABASE_DB_PASSWORD=your_database_password_here")
        print("\nYou can find this in:")
        print("Supabase Dashboard > Settings > Database > Connection String")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n✗ Error loading configuration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
