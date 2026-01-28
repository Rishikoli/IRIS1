
import asyncio
import time
import logging
from typing import Any, Callable, Coroutine, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiRateLimiter:
    """
    Utility to manage Gemini API rate limits with key rotation and backoff.
    """
    def __init__(self, keys: List[str], rpm_limit_per_key: int = 5):
        self.keys = keys
        self.rpm_limit = rpm_limit_per_key
        self.semaphores = {key: asyncio.Semaphore(1) for key in keys}
        self.last_call_time = {key: 0.0 for key in keys}
        self.min_interval = 60.0 / rpm_limit_per_key if rpm_limit_per_key > 0 else 12.0

    async def execute_with_retry(self, 
                               func: Callable[[genai.GenerativeModel], Any], 
                               model_name: str,
                               generation_config: Optional[Any] = None) -> Any:
        last_error = None
        
        # Try each key
        for key in self.keys:
            async with self.semaphores[key]:
                # Implement a minimal delay to respect RPM even before hitting 429
                elapsed = time.time() - self.last_call_time[key]
                if elapsed < self.min_interval:
                    await asyncio.sleep(self.min_interval - elapsed)
                
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel(model_name, generation_config=generation_config)
                    
                    # Run the synchronous generate_content in a thread
                    response = await asyncio.to_thread(func, model)
                    
                    self.last_call_time[key] = time.time()
                    return response
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    if "429" in error_msg or "Resource has been exhausted" in error_msg:
                        logger.warning(f"Rate limit hit for key ending in ...{key[-4:]}, trying next key...")
                        continue
                    else:
                        logger.error(f"Gemini error with key ending in ...{key[-4:]}: {error_msg}")
                        continue
        
        raise last_error

# Global rate limiter instance
from src.config import settings
gemini_limiter = GeminiRateLimiter(settings.gemini_keys, rpm_limit_per_key=5)
