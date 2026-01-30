import requests
import json

def test_network_endpoint():
    companies = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "INVALID_SYMBOL"]
    
    for symbol in companies:
        url = f"http://localhost:8000/api/forensic/network/{symbol}"
        print(f"\nTesting {symbol}...")
        try:
            response = requests.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Success!")
                print(f"Has gemini_data: {'gemini_data' in data}")
                print(f"Has predictive_forensics: {'predictive_forensics' in data}")
            else:
                print("Error Response:")
                print(response.text)
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_network_endpoint()
