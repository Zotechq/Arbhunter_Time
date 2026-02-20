# betika_scraper.py - WITH TIMEZONE CONVERSION
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import re
import json


def convert_to_kenya_time(time_str):
    """
    Convert time from GMT to Kenya time (GMT+3)
    If time is 10:00 GMT, returns 13:00 EAT
    """
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        kenya_time = time_obj + timedelta(hours=3)
        return kenya_time.strftime('%H:%M')
    except:
        return time_str


def fetch_betika_matches(headless=True):
    """
    Fetch football matches from Betika Kenya with proper timezone conversion
    """

    print("=" * 70)
    print("⚽ FETCHING BETIKA KENYA FOOTBALL MATCHES")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        url = "https://www.betika.com/en-ke/s/soccer"
        print(f"\n📡 Loading Betika football page...")
        driver.get(url)
        time.sleep(8)

        # Handle any popups
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
            close_btn.click()
            print("✅ Closed popup")
            time.sleep(2)
        except:
            pass

        # Scroll to load matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get page text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = page_text.split('\n')

        print(f"\n📦 Scanning for match containers...")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for league pattern (contains "•")
            if '•' in line and not re.search(r'\d+\.\d+', line):
                league = line.strip()

                # Next line should have date/time
                if i + 1 < len(lines):
                    time_line = lines[i + 1].strip()
                    time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', time_line)

                    if time_match:
                        date = time_match.group(1)
                        gmt_time = time_match.group(2)  # Original time (likely UTC)

                        # CONVERT TO KENYA TIME
                        kenya_time = convert_to_kenya_time(gmt_time)

                        # Next line should have home team (may have dots)
                        if i + 2 < len(lines):
                            home_line = lines[i + 2].strip()

                            # Clean home team name
                            home = re.sub(r'\.\.\.$', '', home_line).strip()

                            # Next line should have away team
                            away = "Unknown"
                            if i + 3 < len(lines):
                                away_candidate = lines[i + 3].strip()
                                # Check if it's a team name (not odds)
                                if not re.match(r'^\d+\.\d+', away_candidate):
                                    away = away_candidate

                            # Validate we have real team names
                            if home and home != "Unknown" and len(home) > 2:
                                match = {
                                    'home': home,
                                    'away': away if away != "Unknown" else home,
                                    'kickoff': kenya_time,  # KENYA TIME
                                    'original_gmt': gmt_time,  # For reference
                                    'date': date,
                                    'league': league,
                                    'bookie': 'Betika'
                                }
                                matches.append(match)
                                print(f"✅ {home:30} vs {away:30} @ {kenya_time} [{date}]")

                                # Skip ahead 4 lines (league, date, home, away)
                                i += 4
                                continue

            i += 1

        print(f"\n📊 Total matches found: {len(matches)}")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        driver.quit()


def save_matches(matches):
    """Save matches to file"""
    if not matches:
        print("❌ No matches to save")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"betika_matches_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")

    csv_filename = filename.replace('.json', '.csv')
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Home Team,Away Team,Kickoff (EAT),Original GMT,Date,League,Bookie\n")
        for match in matches:
            f.write(
                f"{match['home']},{match['away']},{match['kickoff']},{match.get('original_gmt', '')},{match['date']},\"{match['league']}\",{match['bookie']}\n")
    print(f"💾 Saved {len(matches)} matches to {csv_filename}")


def quick_test():
    """Quick test function"""
    print("🔧 TESTING BETIKA FOOTBALL SCRAPER")
    print("-" * 50)

    matches = fetch_betika_matches(headless=False)

    if matches:
        print(f"\n✅ Betika: {len(matches)} valid matches with kickoff times")
        save_matches(matches)
    else:
        print("\n❌ No matches found")


if __name__ == "__main__":
    quick_test()