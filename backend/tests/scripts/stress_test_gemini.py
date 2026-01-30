
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
        print(f"Request {i+1}: Success ({end-start:.2f}s)")
        return True
    except Exception as e:
        end = time.time()
        print(f"Request {i+1}: FAILED after {end-start:.2f}s - {e}")
        return False

async def stress_test():
    print(f"--- Gemini Rate Limit Test (Model: {settings.gemini_model_name}) ---")
    
    key = settings.gemini_api_key
    if not key:
        print("❌ No API key found.")
        return

    genai.configure(api_key=key)
    model = genai.GenerativeModel(settings.gemini_model_name)
    
    tasks = []
    # Fire off 20 requests in 1 second to surely hit the 15 RPM limit if on free tier
    for i in range(20):
        tasks.append(test_request(model, i))
    
    results = await asyncio.gather(*tasks)
    success_count = sum(results)
    print(f"\nSummary: {success_count}/20 requests succeeded.")
    
    if success_count < 20:
        print("⚠️ Rate limit detected. If success count is around 15 or less, you are likely on the Free Tier (15 RPM limit).")
    else:
        print("✅ No rate limit hit at 20 concurrent requests. You might be on the Paid Tier.")

if __name__ == "__main__":
    asyncio.run(stress_test())
