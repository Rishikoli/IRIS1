#!/usr/bin/env python3
"""
Enhanced example usage of the rate-limited Yahoo Finance client with better error handling.
"""
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_clients.yfinance_client import yfinance_client

def test_historical_data(ticker: str, period: str = "1mo", interval: str = "1d"):
    """Test fetching historical data for a ticker."""
    print(f"\n{'='*50}")
    print(f"Testing historical data for {ticker}...")
    print(f"Period: {period}, Interval: {interval}")
    print("-" * 50)
    
    try:
        data = yfinance_client.get_historical_data(
            ticker=ticker,
            period=period,
            interval=interval
        )
        
        if not data:
            print("No data returned")
            return
            
        # Convert to DataFrame for better display
        df = pd.DataFrame(data)
        print(f"\nSuccess! Retrieved {len(df)} data points for {ticker}:")
        print("Latest data points:")
        print(df.tail())
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        
        # Try to find similar tickers if the requested one fails
        if "not found" in str(e).lower():
            print(f"\nSearching for similar tickers to '{ticker}'...")
            try:
                similar = yfinance_client.search_tickers(ticker.rsplit('.', 1)[0])
                if similar:
                    print("\nDid you mean one of these?")
                    for i, ticker_info in enumerate(similar[:5], 1):
                        print(f"{i}. {ticker_info.get('symbol')} - {ticker_info.get('longname', 'N/A')}")
                else:
                    print("No similar tickers found.")
            except Exception as search_error:
                print(f"Error searching for similar tickers: {str(search_error)}")

def test_ticker_info(ticker: str):
    """Test fetching ticker information."""
    print(f"\n{'='*50}")
    print(f"Testing ticker info for {ticker}...")
    print("-" * 50)
    
    try:
        info = yfinance_client.get_ticker_info(ticker)
        
        print("\nTicker Information:")
        print("-" * 30)
        
        # Display basic info
        basic_info = {
            'Name': info.get('longName', 'N/A'),
            'Symbol': info.get('symbol', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': f"{info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else 'N/A',
            'Current Price': f"{info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))} {info.get('currency', '')}",
            '52-Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52-Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A'
        }
        
        for key, value in basic_info.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Error getting info for {ticker}: {str(e)}")

def main():
    # Test with various tickers and scenarios
    test_cases = [
        # Format: (ticker, period, interval, has_options)
        ("IDEA.NS", "1mo", "1d", False),
        ("RELIANCE.NS", "3mo", "1d", True),
        ("TCS.NS", "1y", "1wk", True),
        ("INVALIDTICKER", "1mo", "1d", False)  # This should fail and trigger ticker search
    ]
    
    for ticker, period, interval, get_options in test_cases:
        test_historical_data(ticker, period, interval)
        
        # Only try to get options data for tickers that support it
        if get_options:
            test_ticker_info(ticker)
    
    # Example of searching for tickers
    search_terms = ["Vodafone", "HDFC"]
    for term in search_terms:
        print(f"\n{'='*50}")
        print(f"Searching for tickers matching: {term}")
        print("-" * 50)
        
        try:
            results = yfinance_client.search_tickers(term)
            if results:
                print(f"\nFound {len(results)} results for '{term}':")
                for i, ticker in enumerate(results[:5], 1):  # Show first 5 results
                    print(f"{i}. {ticker.get('symbol', 'N/A')} - {ticker.get('longname', 'N/A')} "
                          f"({ticker.get('exchange', 'N/A')} - {ticker.get('quoteType', 'N/A')})")
            else:
                print(f"No results found for '{term}'")
        except Exception as e:
            print(f"Error searching for '{term}': {str(e)}")

if __name__ == "__main__":
    print("Yahoo Finance API Tester")
    print("=" * 50)
    print("This script tests various aspects of the Yahoo Finance API client.")
    print("It will try to fetch historical data and ticker information for multiple stocks.")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    
    print("\nTesting complete.")
