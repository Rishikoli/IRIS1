import yfinance as yf
import json

def check_holders(symbol):
    print(f"Checking data for {symbol}...")
    ticker = yf.Ticker(symbol)
    
    data = {}
    
    try:
        # Major Holders
        if ticker.major_holders is not None:
            data['major_holders'] = ticker.major_holders.to_dict()
        else:
            data['major_holders'] = "Not Available"
            
        # Institutional Holders
        if ticker.institutional_holders is not None:
            data['institutional_holders'] = ticker.institutional_holders.head().to_dict()
        else:
            data['institutional_holders'] = "Not Available"
            
        # Mutual Fund Holders
        if ticker.mutualfund_holders is not None:
            data['mutualfund_holders'] = ticker.mutualfund_holders.head().to_dict()
        else:
            data['mutualfund_holders'] = "Not Available"

        # Insider Roster (if available)
        try:
            if ticker.insider_roster_holders is not None:
                data['insiders'] = ticker.insider_roster_holders.head().to_dict()
        except:
            data['insiders'] = "Not Available/Error"

    except Exception as e:
        print(f"Error: {e}")
        
    print(json.dumps(str(data), indent=2))

if __name__ == "__main__":
    check_holders("RELIANCE.NS")
