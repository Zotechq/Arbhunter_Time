# betika_matches.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import json


def fetch_betika_matches(headless=True):
    """
    Fetch soccer matches from Betika using Selenium

    Args:
        headless (bool): Run browser in background if True

    Returns:
        list: List of match dictionaries with home, away, date, time
    """

    print("=" * 60)
    print("⚽ FETCHING BETIKA MATCHES")
    print("=" * 60)

    # Configure Firefox
    options = Options()
    if headless:
        options.add_argument("--headless")
        print("🚀 Running in headless mode (browser invisible)")
    else:
        print("🚀 Opening visible browser window")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0")

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        # Load the page
        url = "https://www.betika.com/en-ke/s/soccer"
        print(f"🌐 Loading {url}...")
        driver.get(url)

        # Wait for matches to load
        print("⏳ Waiting for matches to load...")
        time.sleep(8)

        # Scroll to trigger any lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Get page text for parsing
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Parse matches line by line
        lines = page_text.split('\n')

        for i, line in enumerate(lines):
            # Look for date/time pattern (e.g., "15/02, 20:30")
            time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', line)
            if time_match:
                date_str = time_match.group(1)
                time_str = time_match.group(2)

                # Check next few lines for team names
                for j in range(1, 4):  # Look ahead up to 3 lines
                    if i + j < len(lines):
                        team_line = lines[i + j].strip()

                        # Look for team patterns (capitalized words)
                        teams = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', team_line)

                        # Filter out common non-team words
                        valid_teams = [t for t in teams if len(t) > 2 and
                                       not any(
                                           word in t.lower() for word in ['upcoming', 'live', 'markets', 'highlights'])]

                        if len(valid_teams) >= 2:
                            match = {
                                'home': valid_teams[0],
                                'away': valid_teams[1],
                                'date': date_str,
                                'time': time_str,
                                'datetime': f"{datetime.now().year}-{date_str.replace('/', '-')} {time_str}",
                                'bookie': 'Betika',
                                'league': lines[i - 1] if i > 0 else 'Unknown'  # Previous line often has league
                            }
                            matches.append(match)
                            print(f"✅ {match['home']} vs {match['away']} @ {date_str} {time_str}")
                            break

        print(f"\n📊 Total matches found: {len(matches)}")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return matches

    finally:
        driver.quit()
        print("🔚 Browser closed")


def save_matches(matches, filename=None):
    """Save matches to JSON file"""
    if not filename:
        filename = f"betika_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"💾 Saved {len(matches)} matches to {filename}")


def display_matches(matches):
    """Pretty print matches"""
    if not matches:
        print("❌ No matches to display")
        return

    print("\n" + "=" * 70)
    print(f"{'HOME':<25} {'AWAY':<25} {'DATE':<10} {'TIME':<5}")
    print("=" * 70)

    for match in matches[:20]:  # Show first 20
        print(f"{match['home'][:24]:<25} {match['away'][:24]:<25} {match['date']:<10} {match['time']:<5}")


if __name__ == "__main__":
    # Run the scraper
    matches = fetch_betika_matches(headless=True)  # Set to False to see the browser

    if matches:
        display_matches(matches)
        save_matches(matches)
    else:
        print("\n❌ No matches extracted. Try setting headless=False to debug.")