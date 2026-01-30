
import requests
import json

URL = "http://localhost:8000/api/forensic"

def reproduce(symbol):
    target = f"{URL}/{symbol}"
    print(f"🚀 Sending POST request to {target}...")
    try:
        response = requests.post(target, json={})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 500:
            print("❌ CAUGHT 500 ERROR!")
            print(response.text[:500])
        else:
             print(f"Response: {response.text[:100]}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    reproduce("IDEA.NS")
    reproduce("INVALID_SYMBOL_XYZ")
    reproduce("")
