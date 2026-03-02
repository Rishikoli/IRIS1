
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
        
        max_overall_retries = 2
        current_retry = 0
        
        while current_retry < max_overall_retries:
            # Try each key in this attempt
            explicit_retry_delay = 0.0
            
            for key in self.keys:
                async with self.semaphores[key]:
                    # Implement a minimal delay to respect RPM even before hitting 429
                    elapsed = time.time() - self.last_call_time[key]
                    if elapsed < self.min_interval:
                        await asyncio.sleep(self.min_interval - elapsed)
                    
                    try:
                        genai.configure(api_key=key)
                        model = genai.GenerativeModel(model_name, generation_config=generation_config)
                        
                        try:
                            # Run the synchronous generate_content in a thread with timeout
                            try:
                                response = await asyncio.wait_for(
                                    asyncio.to_thread(func, model),
                                    timeout=25.0 # Individual call timeout
                                )
                                return response
                            except asyncio.TimeoutError:
                                logger.error(f"Gemini API call timed out for key ending in ...{key[-4:]}")
                                raise Exception("Gemini API call timed out")
                        finally:
                            self.last_call_time[key] = time.time()
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg or "Resource has been exhausted" in error_msg:
                            logger.warning(f"Rate limit hit for key ending in ...{key[-4:]}")
                            
                            # Try to extract retry delay from error message
                            import re
                            # Match variants like "retry in 8.97s" or "after 8s"
                            match = re.search(r"retry (?:in|after) (\d+(\.\d+)?)s?", error_msg)
                            if match:
                                delay = float(match.group(1))
                                explicit_retry_delay = max(explicit_retry_delay, delay)
                                
                            continue # Try next key
                        else:
                            # Non-retriable error
                            logger.error(f"Gemini error with key ending in ...{key[-4:]}: {error_msg}")
                            raise e

            # If we are here, it means all keys failed with 429 (or were skipped) in this pass
            current_retry += 1
            if current_retry < max_overall_retries:
                # Calculate wait time:
                # 1. Use explicit delay if server provided it (plus buffer)
                # 2. Otherwise use exponential backoff: 1s, 2s... (Reduced for interactive)
                
                if explicit_retry_delay > 0:
                    wait_time = min(explicit_retry_delay + 1.0, 5.0) # Cap at 5s
                    logger.warning(f"Server requested wait. Sleeping {wait_time:.2f}s before retry {current_retry}/{max_overall_retries}...")
                else:
                    wait_time = min(1.0 * (2 ** (current_retry - 1)), 5.0) # Cap at 5s
                    logger.warning(f"Exponential backoff. Sleeping {wait_time:.2f}s before retry {current_retry}/{max_overall_retries}...")
                
                await asyncio.sleep(wait_time)
            else:
                logger.error("Max retries exceeded. All keys rate limited.")
                raise Exception("Gemini API rate limit exceeded on all keys after retries.")

# Global rate limiter instance
from src.config import settings
gemini_limiter = GeminiRateLimiter(settings.gemini_keys, rpm_limit_per_key=5)
