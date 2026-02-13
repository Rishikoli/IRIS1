
import logging
import aiohttp
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LocalClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama3" # Default to llama3 if not specified
        
    async def check_availability(self) -> bool:
        """Check if Ollama is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama check failed: {e}")
            return False

    async def generate_content(self, prompt: str, model_name: Optional[str] = None) -> str:
        """Generate content using Ollama"""
        model = model_name or self.default_model
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama generation failed: {response.status} - {error_text}")
                        raise Exception(f"Ollama Error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            raise e
