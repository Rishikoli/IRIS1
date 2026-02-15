
import asyncio
import logging
from src.utils.gemini_client import GeminiClient
from src.config import settings

# Configure logging to see rate limiter output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rate_limiting():
    client = GeminiClient()
    
    print(f"Testing GeminiClient with {len(settings.gemini_keys)} keys configured.")
    print("Sending 10 concurrent requests to trigger rate limiter...")
    
    prompt = "Reply with 'OK'"
    
    tasks = []
    for i in range(10):
        tasks.append(client.generate_content(f"{prompt} {i}", use_cache=False))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = 0
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"Request {i} FAILED: {res}")
        else:
            print(f"Request {i} SUCCESS: {res}")
            success_count += 1
            
    print(f"\nSuccess Rate: {success_count}/10")

if __name__ == "__main__":
    asyncio.run(test_rate_limiting())
