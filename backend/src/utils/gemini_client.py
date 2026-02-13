
import os
import json
import hashlib
import logging
import asyncio
from typing import Any, Dict, Optional, Union
from datetime import datetime
import google.generativeai as genai
from src.config import settings
from src.utils.rate_limiter import gemini_limiter

logger = logging.getLogger(__name__)

from src.utils.local_client import LocalClient

class GeminiClient:
    """
    Centralized client for Gemini API calls with:
    1. Automatic Key Rotation (via GeminiRateLimiter)
    2. File-based Caching (to save tokens on repeated queries)
    3. Unified Error Handling
    4. Local Model Fallback (Ollama)
    """
    
    def __init__(self, cache_dir: str = "./data/cache/gemini"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        self.local_client = LocalClient(base_url=settings.local_llm_url)
        
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _generate_cache_key(self, prompt: str, model_name: str) -> str:
        """Generate a unique cache key based on prompt and model"""
        content = f"{model_name}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve response from cache if it exists"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Optional: Check TTL if needed, but for now we assume persistent cache for analysis
                    logger.info(f"Cache hit for key {cache_key}")
                    return data
            except Exception as e:
                logger.warning(f"Failed to read cache file {cache_file}: {e}")
        return None
        
    def _save_to_cache(self, cache_key: str, response_text: str):
        """Save response to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "response": response_text
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.debug(f"Saved response to cache {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save to cache {cache_file}: {e}")

    async def generate_content(self, 
                             prompt: str, 
                             model_name: Optional[str] = None,
                             generation_config: Optional[Any] = None,
                             use_cache: bool = True) -> str:
        """
        Generate content using Gemini with automatic rate limiting, caching, and local fallback.
        
        Args:
            prompt: The input text prompt
            model_name: Optional custom model name (defaults to settings)
            generation_config: Optional generation config
            use_cache: Whether to use cached responses (default: True)
            
        Returns:
            The generated text response
        """
        model_name = model_name or settings.gemini_model_name
        
        # 1. Check Cache
        if use_cache:
            cache_key = self._generate_cache_key(prompt, model_name)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data["response"]
        
        # 2. Call API via Rate Limiter
        try:
            # wrapper function to be called by rate limiter
            def _api_call(model: genai.GenerativeModel):
                return model.generate_content(prompt)
                
            response = await gemini_limiter.execute_with_retry(
                _api_call,
                model_name=model_name,
                generation_config=generation_config
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
                
            text_response = response.text.strip()
            
            # 3. Save to Cache
            if use_cache:
                self._save_to_cache(cache_key, text_response)
                
            return text_response
            
        except Exception as e:
            logger.error(f"GeminiClient generation failed: {str(e)}")
            
            # 4. Fallback to Local LLM
            if settings.enable_local_llm_fallback:
                logger.warning("Attempting fallback to Local LLM (Ollama)...")
                try:
                    text_response = await self.local_client.generate_content(
                        prompt, 
                        model_name=settings.local_llm_model
                    )
                    logger.info("Local LLM fallback successful")
                    
                    # Optional: Cache local result? 
                    # Yes, prevent re-generation locally too.
                    if use_cache:
                        # We use the same cache key so next time it just loads this result
                        # effectively masking the API failure persistently for this prompt
                        self._save_to_cache(cache_key, text_response)
                        
                    return text_response
                except Exception as local_e:
                    logger.error(f"Local LLM fallback also failed: {local_e}")
                    raise e # Raise original Gemini error if local fails too
            
            raise e

# Global instance
gemini_client = GeminiClient()
