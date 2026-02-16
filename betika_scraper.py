# betika_scraper_fixed_js.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
import json


def fetch_betika_matches(headless=True):
    """
    Get Betika matches - WAITS for JavaScript to update times
    """

    print("=" * 70)
    print("⚽ FETCHING BETIKA MATCHES (JS WAIT)")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        print("\n📡 Loading Betika...")
        driver.get("https://www.betika.com/en-ke/s/soccer")

        # Wait longer for JavaScript to modify times
        print("⏳ Waiting 15 seconds for JavaScript to update times...")
        time.sleep(15)

        # Scroll to load all matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # Get the main content area
        try:
            content = driver.find_element(By.CLASS_NAME, "desktop-layout__content")
            page_text = content.text
        except:
            page_text = driver.find_element(By.TAG_NAME, "body").text

        lines = page_text.split('\n')

        print("\n🔍 Extracting matches with kickoff times...")
        print("-" * 70)

        # Find Macclesfield match specifically
        for line in lines:
            if 'Macclesfield' in line and 'Brentford' in line:
                print(f"\n🔍 Found Macclesfield line: {line}")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for league + time pattern
            if '•' in line:
                league = line
                if i + 1 < len(lines):
                    time_line = lines[i + 1].strip()
                    time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', time_line)

                    if time_match:
                        date = time_match.group(1)
                        kickoff = time_match.group(2)

                        if i + 2 < len(lines) and i + 3 < len(lines):
                            home = lines[i + 2].strip()
                            away = lines[i + 3].strip()

                            home = re.sub(r'\.\.\.$', '', home).strip()
                            away = re.sub(r'\.\.\.$', '', away).strip()

                            if home and away:
                                match = {
                                    'home': home,
                                    'away': away,
                                    'kickoff': kickoff,
                                    'date': date,
                                    'league': league,
                                    'bookie': 'Betika'
                                }
                                matches.append(match)
                                print(f"✅ {home:30} vs {away:30} @ {kickoff}")
                                i += 4
                                continue

            i += 1

        print(f"\n📊 Found {len(matches)} matches")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

    finally:
        driver.quit()