
import os
import sys
import time
import asyncio
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

async def test_request(model, i):
    start = time.time()
    try:
        response = await asyncio.to_thread(model.generate_content, "Hi")
        end = time.time()
        # print(f"Request {i+1}: Success ({end-start:.2f}s)")
        return True
    except Exception as e:
        print(f"Request {i+1} ({model.model_name}): FAILED - {e}")
        if "429" in str(e):
             return "429"
        return False

async def stress_test_model(model_name):
    print(f"\n--- Testing Rate Limit for: {model_name} ---")
    
    key = settings.gemini_api_key
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name)
    
    tasks = []
    for i in range(20):
        tasks.append(test_request(model, i))
    
    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r is True)
    ratelimit_count = sum(1 for r in results if r == "429")
    
    print(f"Summary for {model_name}: {success_count}/20 succeeded, {ratelimit_count} hit 429.")
    return success_count

async def main():
    await stress_test_model("gemini-1.5-flash")
    await stress_test_model("gemini-2.0-flash-exp")

if __name__ == "__main__":
    asyncio.run(main())
