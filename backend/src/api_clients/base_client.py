"""
Project IRIS - Base API Client
Common functionality for external API clients
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from src.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60, calls_per_day: int = 1000):
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_calls = []
        self.day_calls = []
        
    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits"""
        now = time.time()
        
        # Clean old calls
        self.minute_calls = [call_time for call_time in self.minute_calls if now - call_time < 60]
        self.day_calls = [call_time for call_time in self.day_calls if now - call_time < 86400]
        
        # Check limits
        if len(self.minute_calls) >= self.calls_per_minute:
            return False
        if len(self.day_calls) >= self.calls_per_day:
            return False
            
        return True
    
    def record_request(self):
        """Record a request"""
        now = time.time()
        self.minute_calls.append(now)
        self.day_calls.append(now)
    
    def wait_time(self) -> float:
        """Get wait time until next request is allowed"""
        if not self.minute_calls and not self.day_calls:
            return 0
            
        now = time.time()
        
        # Check minute limit
        if len(self.minute_calls) >= self.calls_per_minute:
            oldest_minute_call = min(self.minute_calls)
            minute_wait = 60 - (now - oldest_minute_call)
            if minute_wait > 0:
                return minute_wait
        
        # Check day limit
        if len(self.day_calls) >= self.calls_per_day:
            oldest_day_call = min(self.day_calls)
            day_wait = 86400 - (now - oldest_day_call)
            if day_wait > 0:
                return day_wait
                
        return 0


class BaseAPIClient(ABC):
    """Base class for external API clients"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 rate_limit_per_minute: int = 60, rate_limit_per_day: int = 1000,
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.rate_limiter = RateLimiter(rate_limit_per_minute, rate_limit_per_day)
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            'User-Agent': 'IRIS-Forensic-Platform/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.api_key:
            self.session.headers.update(self._get_auth_headers())
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for the API"""
        pass
    
    def _wait_for_rate_limit(self):
        """Wait if rate limit is exceeded"""
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with rate limiting and error handling"""
        
        # Wait for rate limit
        self._wait_for_rate_limit()
        
        # Prepare request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            
            # Record successful request
            self.rate_limiter.record_request()
            
            # Handle response
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited by server, waiting {retry_after} seconds")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data, headers)
            
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw_response": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            logger.error(f"URL: {url}")
            logger.error(f"Params: {params}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request("GET", endpoint, params=params, headers=headers)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, 
             headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._make_request("POST", endpoint, params=params, data=data, headers=headers)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None,
            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._make_request("PUT", endpoint, params=params, data=data, headers=headers)
    
    def delete(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._make_request("DELETE", endpoint, params=params, headers=headers)
    
    def health_check(self) -> bool:
        """Check if the API is accessible"""
        try:
            response = self.get("/")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test API connection with a simple request"""
        pass
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            "calls_per_minute_limit": self.rate_limiter.calls_per_minute,
            "calls_per_day_limit": self.rate_limiter.calls_per_day,
            "calls_this_minute": len(self.rate_limiter.minute_calls),
            "calls_today": len(self.rate_limiter.day_calls),
            "can_make_request": self.rate_limiter.can_make_request(),
            "wait_time_seconds": self.rate_limiter.wait_time()
        }
