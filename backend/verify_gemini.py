
import sys
import os
from pathlib import Path
import pprint

# Add backend to python path
backend_path = Path("/home/aditya/Downloads/IRIS/backend")
sys.path.append(str(backend_path))

try:
    from src.config import settings
    import google.generativeai as genai
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def list_models():
    print("Checking Gemini API Models...")
    
    keys = settings.gemini_keys
    if not keys:
        print("❌ No Gemini API keys found.")
        return

    # Use first key to list models
    key = keys[0]
    print(f"Using Key: ...{key[-4:]}")
    
    try:
        genai.configure(api_key=key)
        
        print("\nAvailable Models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                
        print("\nNow testing a simple generation with a discovered model...")
        # Try to find a flash model or pro model
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m.name for m in models if 'flash' in m.name), None)
        if not target_model:
            target_model = next((m.name for m in models if 'gemini' in m.name), None)
            
        if target_model:
            print(f"Testing with: {target_model}")
            model = genai.GenerativeModel(target_model)
            response = model.generate_content("Hello")
            print(f"✅ Response received: {response.text.strip()}")
        else:
            print("⚠️ No suitable generation model found.")

    except Exception as e:
        print(f"❌ Error listing/testing models: {e}")

if __name__ == "__main__":
    list_models()
