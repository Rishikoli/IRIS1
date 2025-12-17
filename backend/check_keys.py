
import sys
import os

# Add backend to path
sys.path.append('/home/aditya/Downloads/IRIS/backend')

from src.config import settings

print(f"Number of Gemini keys found: {len(settings.gemini_keys)}")
for i, key in enumerate(settings.gemini_keys):
    print(f"Key {i+1}: ...{key[-4:] if key else 'None'}")
