
import os
import sys
from pathlib import Path

# Add the current directory to sys.path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

try:
    from src.config import settings
    import google.generativeai as genai
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def list_models():
    key = settings.gemini_api_key
    genai.configure(api_key=key)
    print("Available GenAI Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (Quotas: {m.quota_period if hasattr(m, 'quota_period') else 'N/A'})")

if __name__ == "__main__":
    list_models()
