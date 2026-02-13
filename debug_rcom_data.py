
import yfinance as yf
import pandas as pd

def debug_rcom_data():
    ticker = yf.Ticker("RCOM.NS")
    
    print("--- Balance Sheet Keys ---")
    bs = ticker.balance_sheet
    if bs is not None:
        for col in bs.columns:
            print(f"Period: {col}")
            print(bs[col].dropna().index.tolist())
            print("-" * 20)
    else:
        print("Balance Sheet is None")

    print("\n--- Income Statement Keys ---")
    is_ = ticker.financials
    if is_ is not None:
        for col in is_.columns:
            print(f"Period: {col}")
            print(is_[col].dropna().index.tolist())
            print("-" * 20)
    else:
        print("Income Statement is None")

if __name__ == "__main__":
    debug_rcom_data()
