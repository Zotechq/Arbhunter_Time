# betika_scraper.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import re
import json
import csv


def fetch_betika_matches():
    """
    Get football matches from Betika with kickoff times
    Returns a list of matches with home, away, kickoff, league
    """

    print("=" * 70)
    print("⚽ FETCHING BETIKA MATCHES WITH KICKOFF TIMES")
    print("=" * 70)

    options = Options()
    options.add_argument("--headless")  # Run in background
    # options.add_argument("--headless")  # Comment this out to see the browser

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        print("\n📡 Loading Betika...")
        driver.get("https://www.betika.com/en-ke/s/soccer")
        time.sleep(8)

        # Scroll to load all matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get the main content area
        try:
            content = driver.find_element(By.CLASS_NAME, "desktop-layout__content")
            page_text = content.text
        except:
            # Fallback to whole page
            page_text = driver.find_element(By.TAG_NAME, "body").text

        lines = page_text.split('\n')

        print("\n🔍 Extracting matches with kickoff times...")
        print("-" * 70)

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for league + date pattern (e.g., "Chile • Primera Division")
            if '•' in line and not re.search(r'\d+\.\d+', line):
                league = line

                # Next line should have date/time
                if i + 1 < len(lines):
                    time_line = lines[i + 1].strip()
                    time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', time_line)

                    if time_match:
                        date = time_match.group(1)
                        kickoff = time_match.group(2)

                        # Next two lines should be teams
                        if i + 2 < len(lines) and i + 3 < len(lines):
                            home = lines[i + 2].strip()
                            away = lines[i + 3].strip()

                            # Clean up team names
                            home = re.sub(r'\.\.\.$', '', home).strip()
                            away = re.sub(r'\.\.\.$', '', away).strip()

                            # Skip if these are odds or not real teams
                            if (home and away and
                                    not re.search(r'\d+\.\d+', home) and
                                    not re.search(r'\d+\.\d+', away) and
                                    len(home) > 2 and len(away) > 2):
                                match = {
                                    'home': home,
                                    'away': away,
                                    'kickoff': kickoff,
                                    'date': date,
                                    'league': league,
                                    'bookie': 'Betika',
                                    'timestamp': f"{datetime.now().year}-{date.replace('/', '-')} {kickoff}"
                                }
                                matches.append(match)
                                print(f"⏰ {home:35} vs {away:35} @ {kickoff} [{league[:30]}]")

                                # Skip ahead 4 lines
                                i += 4
                                continue

            i += 1

        print(f"\n📊 Found {len(matches)} matches with kickoff times")
        return matches

    except Exception as e:
        print(f"❌ Error in Betika scraper: {e}")
        return []

    finally:
        driver.quit()


def save_matches(matches, format='both'):
    """Save matches to file"""
    if not matches:
        print("❌ No matches to save")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if format in ['json', 'both']:
        json_filename = f"betika_matches_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {json_filename}")

    if format in ['csv', 'both']:
        csv_filename = f"betika_matches_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Home Team', 'Away Team', 'Kickoff', 'Date', 'League', 'Bookie'])
            for match in matches:
                writer.writerow([
                    match['home'],
                    match['away'],
                    match['kickoff'],
                    match['date'],
                    match['league'],
                    match['bookie']
                ])
        print(f"💾 Saved to {csv_filename}")


def display_matches(matches):
    """Display matches in a clean table"""
    if not matches:
        print("\n❌ No matches to display")
        return

    print("\n" + "=" * 100)
    print(f"📋 BETIKA MATCHES - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 100)
    print(f"{'#':<3} {'HOME TEAM':<35} {'AWAY TEAM':<35} {'KICKOFF':<8} {'LEAGUE':<20}")
    print("-" * 100)

    # Sort by kickoff time
    sorted_matches = sorted(matches, key=lambda x: x['kickoff'])

    for i, match in enumerate(sorted_matches, 1):
        league_short = match['league'][:19] if len(match['league']) > 19 else match['league']
        print(f"{i:<3} {match['home'][:34]:<35} {match['away'][:34]:<35} {match['kickoff']:<8} {league_short:<20}")

    print("=" * 100)
    print(f"Total: {len(matches)} matches")


if __name__ == "__main__":
    # If run directly, just test the scraper
    matches = fetch_betika_matches()
    if matches:
        display_matches(matches)
        save_matches(matches)
    else:
        print("❌ No matches found")