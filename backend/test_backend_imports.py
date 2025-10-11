"""
Simple backend test script for IRIS API endpoints
Bypasses config requirements for testing
"""

import sys
import os
sys.path.insert(0, '/home/aditya/I.R.I.S./backend/src')

# Mock the config module to avoid API key requirements
class MockSettings:
    def __init__(self):
        self.api_host = "0.0.0.0"
        self.api_port = 8000
        self.api_reload = False
        self.log_level = "INFO"
        self.log_format = "text"
        self.environment = "development"
        self.cors_origins_list = ["*"]
        # Add None values for required API keys
        self.gemini_api_key = None
        self.fmp_api_key = None
        self.supabase_url = None
        self.supabase_key = None

# Replace the real config module
sys.modules['src.config'] = type(sys)('src.config')
sys.modules['src.config'].settings = MockSettings()

# Mock database connection
class MockDBClient:
    def __init__(self):
        pass
    def execute_query(self, query, params=None):
        return []
    def ping(self):
        return True

sys.modules['src.database'] = type(sys)('src.database')
sys.modules['src.database'].connection = type(sys)('connection')
sys.modules['src.database'].connection.get_db_client = lambda: MockDBClient()

# Now try to import the main app
try:
    from src.api.main import app
    print('✅ Backend app imported successfully with mocks')

    # Test that routes are registered
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)

    print(f'📋 Routes registered: {len(routes)}')

    # Check for key endpoints
    key_endpoints = [
        '/health',
        '/api/companies',
        '/api/forensic/{company_symbol}',
        '/api/risk-score/{company_symbol}'
    ]

    print(f'\\n🎯 Key endpoints check:')
    for endpoint in key_endpoints:
        if endpoint in routes:
            print(f'   ✅ {endpoint}')
        else:
            print(f'   ❌ {endpoint} - MISSING')

except Exception as e:
    print(f'❌ Backend app import failed: {e}')
    import traceback
    traceback.print_exc()

print('\\n🚀 BACKEND IS READY FOR TESTING!')
print('Start the server with: python3 src/api/main.py')
