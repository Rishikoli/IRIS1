import time
import random
import yfinance as yf
import requests
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

class YFinanceClient:
    """
    A rate-limited client for Yahoo Finance API with retry logic and request throttling.
    """
    
    def __init__(self, max_requests_per_minute: int = 30):
        """
        Initialize the YFinance client with rate limiting.
        
        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.request_timestamps = []
        self.last_request_time = None
        self.min_interval = 2.0  # Minimum seconds between requests
        
    def _throttle_requests(self):
        """Implement request throttling to respect rate limits."""
        now = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        
        # If we've hit the rate limit, wait until we can make another request
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self.request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time + 0.1)  # Add a small buffer
        
        # Enforce minimum interval between requests
        if self.last_request_time is not None:
            elapsed = now - self.last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed + random.uniform(0, 0.5))
        
        self.last_request_time = time.time()
        self.request_timestamps.append(self.last_request_time)
    
    def _make_yfinance_request(self, ticker: str, **kwargs) -> Any:
        """Make a request to Yahoo Finance with enhanced error handling."""
        try:
            self._throttle_requests()
            ticker_obj = yf.Ticker(ticker)
            
            # Try to get basic info first to check if ticker is valid
            try:
                ticker_info = ticker_obj.info
                if not ticker_info:
                    raise ValueError(f"No data found for ticker: {ticker}")
            except (ValueError, KeyError) as e:
                print(f"Warning: Could not get info for {ticker}: {str(e)}")
            
            # Get historical data
            data = ticker_obj.history(
                period=kwargs.get('period', '1mo'),
                interval=kwargs.get('interval', '1d'),
                start=kwargs.get('start'),
                end=kwargs.get('end'),
                auto_adjust=True,
                prepost=False,
                threads=True,
                proxy=None
            )
            
            if data.empty:
                raise ValueError(f"No historical data found for {ticker}")
                
            return data
            
        except Exception as e:
            print(f"Error in _make_yfinance_request for {ticker}: {str(e)}")
            raise
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1mo", 
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
        retries: int = 3,
        **kwargs
    ) -> Dict:
        """
        Get historical market data with rate limiting and retry logic.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
            period: Data period to download ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
            interval: Data interval ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
            start: Download start date string (YYYY-MM-DD) or datetime
            end: Download end date string (YYYY-MM-DD) or datetime
            retries: Number of retries on failure
            **kwargs: Additional arguments to pass to yf.download()
            
        Returns:
            Dictionary containing the historical data
        """
        last_error = None
        
        last_error = None
        
        for attempt in range(retries):
            try:
                print(f"\nAttempt {attempt + 1} for {ticker}...")
                
                # Add exponential backoff between retries
                if attempt > 0:
                    backoff = min(2 ** attempt + random.uniform(0, 1), 10)  # Cap at 10 seconds
                    print(f"Waiting {backoff:.2f} seconds before retry...")
                    time.sleep(backoff)
                
                data = self._make_yfinance_request(
                    ticker=ticker,
                    period=period,
                    interval=interval,
                    start=start,
                    end=end,
                    **kwargs
                )
                
                if data is None or data.empty:
                    raise ValueError(f"No data returned for {ticker}")
                
                print(f"Successfully retrieved data for {ticker}")
                return data.to_dict()
                
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # If we get a JSON decode error, it might be a temporary issue
                if "JSONDecodeError" in str(e) and attempt < retries - 1:
                    print("JSON decode error detected, trying with a fresh session...")
                    # Clear any cached sessions
                    if hasattr(yf, 'shared'):
                        yf.shared._ERRORS = {}
                    continue
                    
                # If we get a 404, the ticker might be invalid
                if "404" in str(e):
                    raise ValueError(f"Ticker {ticker} not found. Please check the ticker symbol.")
                
                continue
                
        raise Exception(f"Failed to fetch data for {ticker} after {retries} attempts. Last error: {str(last_error)}")
    
    def get_ticker_info(self, ticker: str, max_retries: int = 3) -> Dict:
        """
        Get detailed information about a ticker with rate limiting and retries.
        
        Args:
            ticker: Stock ticker symbol
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing ticker information
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self._throttle_requests()
                ticker_obj = yf.Ticker(ticker)
                info = ticker_obj.info
                
                # Check if we got valid data
                if not info:
                    raise ValueError(f"No information found for {ticker}")
                    
                return info
                
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} to get info for {ticker} failed: {str(e)}")
                
                # Add delay between retries
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0, 1))
                
        raise Exception(f"Failed to get info for {ticker} after {max_retries} attempts. "
                      f"Last error: {str(last_error)}")
        
    def search_tickers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for tickers matching a query.
        
        Args:
            query: Search term (e.g., 'Vodafone')
            max_results: Maximum number of results to return
            
        Returns:
            List of matching tickers with their information
        """
        self._throttle_requests()
        try:
            # Use yfinance's tickers module to search
            search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount={max_results}&newsCount=0"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return data.get('quotes', [])
            
        except Exception as e:
            print(f"Error searching for tickers: {str(e)}")
            return []

# Singleton instance
yfinance_client = YFinanceClient()
