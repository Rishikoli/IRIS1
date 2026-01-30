
import os
import sys
from pathlib import Path

# Add project root to path (backend/)
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

try:
    from src.config import settings
    import google.generativeai as genai
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_gemini_3():
    model_name = "gemini-3-flash-preview"
    print(f"Testing model: {model_name}")
    
    keys = settings.gemini_keys
    if not keys:
        print("No Gemini API keys found in settings.")
        return

    for i, key in enumerate(keys):
        print(f"Trying key {i+1}/{len(keys)} (ending in ...{key[-4:] if key else 'None'})...")
        if not key:
            continue
            
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, can you confirm you are Gemini 3 Flash Preview?")
            
            print("\n--- SUCCESS ---")
            print(f"Response: {response.text}")
            print("---------------")
            return
        except Exception as e:
            print(f"Failed with key {i+1}: {e}")

    print("\nAll keys failed.")

if __name__ == "__main__":
    test_gemini_3()
