
import requests
import json

BASE_URL = "http://localhost:8000"
COMPANY = "RELIANCE"

def test_network_endpoint():
    print(f"Testing endpoint: {BASE_URL}/api/forensic/network/{COMPANY}")
    try:
        response = requests.get(f"{BASE_URL}/api/forensic/network/{COMPANY}")
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=2))
        except:
            print("Response Text:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_network_endpoint()
