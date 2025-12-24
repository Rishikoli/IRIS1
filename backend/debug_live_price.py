
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def check_live_data():
    symbol = "IDEA.NS"
    print(f"Fetching live 1-minute data for {symbol}...")
    
    try:
        # Fetch 1-minute data for the last 1 day (or limited peroid)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        
        if data.empty:
            print("No intraday data received.")
            return

        print(f"Received {len(data)} rows of data.")
        print("Last 5 rows:")
        print(data.tail())
        
        # Check for latest timestamp
        last_time = data.index[-1]
        print(f"\nLatest data point: {last_time}")
        
        # Simple Anomaly Logic Test
        # Anomaly if Volume > 2 * Mean Volume
        mean_vol = data['Volume'].mean()
        current_vol = data['Volume'].iloc[-1]
        
        print(f"\nMean Volume (5m): {mean_vol:,.0f}")
        print(f"Current Volume: {current_vol:,.0f}")
        
        if current_vol > 2 * mean_vol:
            print("ANOMALY: High Volume Detected!")
        else:
            print("Volume Normal.")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    check_live_data()
