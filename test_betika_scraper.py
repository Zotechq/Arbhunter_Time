# betika_final_working.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import json


def fetch_betika_matches_final(headless=True):
    """
    FINAL WORKING VERSION - Extracts matches using the correct pattern
    """

    print("=" * 60)
    print("⚽ BETIKA MATCH EXTRACTOR - FINAL WORKING VERSION")
    print("=" * 60)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        print("🌐 Loading Betika...")
        driver.get("https://www.betika.com/en-ke/s/soccer")

        # Wait for page to load
        time.sleep(8)

        # Scroll to load all matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get the main content area (desktop-layout__content)
        content = driver.find_element(By.CLASS_NAME, "desktop-layout__content")
        page_text = content.text
        lines = page_text.split('\n')

        print("📊 Parsing matches...")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for league pattern (e.g., "Chile • Primera Division")
            if '•' in line and not re.search(r'\d+\.\d+', line):
                league = line

                # Next line should be date/time
                if i + 1 < len(lines):
                    time_line = lines[i + 1].strip()
                    time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', time_line)

                    if time_match:
                        date_str = time_match.group(1)
                        time_str = time_match.group(2)

                        # Next two lines should be team names
                        if i + 2 < len(lines) and i + 3 < len(lines):
                            home = lines[i + 2].strip()
                            away = lines[i + 3].strip()

                            # Clean up team names
                            home = re.sub(r'\.\.\.$', '', home).strip()
                            away = re.sub(r'\.\.\.$', '', away).strip()

                            # Skip if these are odds (contain numbers)
                            if not re.search(r'\d+\.\d+', home) and not re.search(r'\d+\.\d+', away):
                                # Parse date with smart year detection
                                match_date = smart_year_detection(date_str, time_str)

                                match = {
                                    'home': home,
                                    'away': away,
                                    'date': date_str,
                                    'time': time_str,
                                    'datetime': match_date.isoformat(),
                                    'league': league,
                                    'bookie': 'Betika'
                                }
                                matches.append(match)
                                print(f"✅ {home:20} vs {away:20} @ {date_str} {time_str}")

                                # Skip ahead 4 lines (league, time, home, away)
                                i += 4
                                continue

            i += 1

        print(f"\n📊 Total matches found: {len(matches)}")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return matches

    finally:
        driver.quit()


def smart_year_detection(date_str, time_str):
    """Intelligently determine the correct year for a match"""
    now = datetime.now()
    current_year = now.year

    try:
        day, month = map(int, date_str.split('/'))
        hour, minute = map(int, time_str.split(':'))

        # Try current year
        match_time = datetime(current_year, month, day, hour, minute)

        # If match is more than 2 months in the past, try next year
        if match_time < now - timedelta(days=60):
            match_time = datetime(current_year + 1, month, day, hour, minute)

        # If match is more than 10 months in the future, try previous year
        elif match_time > now + timedelta(days=300):
            match_time = datetime(current_year - 1, month, day, hour, minute)

        return match_time

    except Exception as e:
        return now


def test_final_scraper():
    """Test the final working scraper"""

    print("=" * 80)
    print("🔬 TESTING FINAL BETIKA SCRAPER")
    print("=" * 80)

    matches = fetch_betika_matches_final(headless=True)

    if matches:
        print(f"\n✅ SUCCESS! Found {len(matches)} matches")

        print("\n📋 All matches:")
        print("-" * 80)
        for i, match in enumerate(matches, 1):
            print(f"{i:2}. {match['home']:25} vs {match['away']:25}")
            print(f"    {match['league']}")
            print(f"    {match['date']} at {match['time']}")
            print()

        # Save to file
        filename = f"betika_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(matches, f, indent=2)
        print(f"💾 Saved to {filename}")

        # Also save as CSV for easy viewing
        csv_filename = f"betika_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w') as f:
            f.write("Home,Away,Date,Time,League\n")
            for match in matches:
                f.write(f"{match['home']},{match['away']},{match['date']},{match['time']},\"{match['league']}\"\n")
        print(f"💾 Saved to {csv_filename}")

    else:
        print("❌ No matches found")


if __name__ == "__main__":
    test_final_scraper()