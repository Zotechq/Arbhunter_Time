# diagnostic_test.py
import requests
from bs4 import BeautifulSoup
import re


def diagnose_odibets():
    """Try different approaches to find where match data lives"""

    base_url = "https://www.odibets.com"

    # URLs to try (common patterns on betting sites)
    urls_to_try = [
        "/sports/soccer",
        "/football",
        "/matches",
        "/events",
        "/live",
        "/odds",
        "/api/matches",  # Sometimes API endpoints are exposed
        "/api/events",
        "/data/matches"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': base_url
    }

    print("🔍 DIAGNOSING ODIBETS STRUCTURE")
    print("=" * 50)

    # First, check if the site uses JavaScript loading
    print("\n📊 Checking page structure...")
    response = requests.get(f"{base_url}/sports/soccer", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for clues about data loading
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and any(word in script.string.lower() for word in ['api', 'match', 'event', 'fixture']):
            print(f"\n✅ Found script with potential API hints:")
            # Print first 200 chars of relevant scripts
            print(script.string[:200])

    # Look for data attributes in HTML
    print("\n🔎 Looking for data containers...")
    data_attrs = soup.find_all(attrs={"data-*": True})
    if data_attrs:
        print(f"Found {len(data_attrs)} elements with data attributes")

    # Try common API patterns
    print("\n🌐 Attempting API endpoints...")
    for path in urls_to_try:
        url = base_url + path
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"\n{url}: Status {resp.status_code}")

            # Check if response is JSON
            if 'application/json' in resp.headers.get('Content-Type', ''):
                print("  ✅ JSON response received!")
                print(f"  Sample: {str(resp.text)[:200]}")
            else:
                # Check if HTML contains match data
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Look for common match indicators
                match_indicators = soup.find_all(class_=re.compile(r'match|event|game|fixture', re.I))
                if match_indicators:
                    print(f"  ✅ Found {len(match_indicators)} potential match elements")

        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    diagnose_odibets()