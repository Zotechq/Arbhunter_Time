# betika_scraper.py - FINAL VERSION
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import re
import json


def fetch_betika_matches(headless=True):
    """
    Fetch soccer matches from Betika - FINAL WORKING VERSION
    """

    print("=" * 60)
    print("⚽ FETCHING BETIKA MATCHES")
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

        # Get the main content area
        content = driver.find_element(By.CLASS_NAME, "desktop-layout__content")
        page_text = content.text
        lines = page_text.split('\n')

        print("📊 Parsing matches...")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for league pattern (contains • and not odds)
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

                            # Skip if these are odds
                            if not re.search(r'\d+\.\d+', home) and not re.search(r'\d+\.\d+', away):
                                # Parse date with smart year detection
                                match_date = parse_match_datetime(date_str, time_str)

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
                                print(f"✅ {home:25} vs {away:25} @ {date_str} {time_str}")

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


def parse_match_datetime(date_str, time_str):
    """Parse date string to datetime with smart year detection"""
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


def save_matches(matches, format='json'):
    """Save matches to file"""
    if not matches:
        print("❌ No matches to save")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if format == 'json':
        filename = f"betika_matches_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(matches, f, indent=2)
        print(f"💾 Saved {len(matches)} matches to {filename}")

    elif format == 'csv':
        filename = f"betika_matches_{timestamp}.csv"
        with open(filename, 'w') as f:
            f.write("Home,Away,Date,Time,League\n")
            for match in matches:
                f.write(f"{match['home']},{match['away']},{match['date']},{match['time']},\"{match['league']}\"\n")
        print(f"💾 Saved {len(matches)} matches to {filename}")


if __name__ == "__main__":
    # Test the scraper
    matches = fetch_betika_matches(headless=True)

    if matches:
        print(f"\n✅ Successfully extracted {len(matches)} matches")
        save_matches(matches, 'json')
        save_matches(matches, 'csv')
    else:
        print("❌ No matches found")