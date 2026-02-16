# test_api_connection.py
import requests
from config import RAPIDAPI_KEY


def test_rapidapi_connection():
    """Simple test to verify RapidAPI connection"""

    print("=" * 60)
    print("🔍 TESTING RAPIDAPI CONNECTION")
    print("=" * 60)

    # Test with a simple endpoint first
    url = "https://flashlive-sports.p.rapidapi.com/v1/sports/list"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "flashlive-sports.p.rapidapi.com"
    }

    print(f"\n📡 Testing connection to: {url}")
    print(f"🔑 Using key: {RAPIDAPI_KEY[:5]}...{RAPIDAPI_KEY[-5:]}")

    try:
        response = requests.get(url, headers=headers)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS! API is working!")
            data = response.json()
            print(f"\n📋 Available sports: {len(data.get('DATA', []))} found")
            return True
        elif response.status_code == 401:
            print("❌ ERROR 401: Unauthorized - Invalid API key")
            print("   Check that your key is correct and you've subscribed to the API")
        elif response.status_code == 403:
            print("❌ ERROR 403: Forbidden - Check your subscription")
        elif response.status_code == 429:
            print("❌ ERROR 429: Too Many Requests - Rate limit exceeded")
        else:
            print(f"❌ ERROR {response.status_code}: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Check your internet")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    return False


if __name__ == "__main__":
    test_rapidapi_connection()