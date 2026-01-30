
import os
import sys
from pathlib import Path

# Add the current directory to sys.path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

try:
    from src.config import settings
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def check_gemini():
    print("--- Gemini API Verification ---")
    
    # Load .env explicitly if needed (though Settings should handle it)
    load_dotenv()
    
    keys = settings.gemini_keys
    if not keys or not keys[0]:
        print("❌ No Gemini API keys found in settings.")
        # Check environment variable directly as a fallback
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key:
            print(f"Found GEMINI_API_KEY in environment directly: ...{env_key[-4:]}")
            keys = [env_key]
        else:
            print("❌ GEMINI_API_KEY not found in environment either.")
            return

    print(f"Found {len(keys)} Gemini API keys.")
    
    for i, key in enumerate(keys):
        print(f"\nTesting Key {i+1}: ...{key[-4:] if key else 'None'}")
        if not key:
            continue
            
        try:
            genai.configure(api_key=key)
            
            print("Listing available models...")
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
            
            if not models:
                print("⚠️ No generation models found for this key.")
                continue
            
            print(f"Available models: {', '.join(models[:5])}...")
            
            # Try to use the configured model
            target_model = settings.gemini_model_name
            print(f"Testing generation with: {target_model}")
            
            model = genai.GenerativeModel(target_model)
            response = model.generate_content("Say 'Gemini API is working!'")
            
            if response and response.text:
                print(f"✅ Success! Response: {response.text.strip()}")
            else:
                print("⚠️ Received empty response.")
                
        except Exception as e:
            print(f"❌ Error with Key {i+1}: {e}")

if __name__ == "__main__":
    check_gemini()
