# mozzartbet_scraper.py - CLEAN OUTPUT WITH KENYA TIME
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
    If time is 17:45 GMT, returns 20:45 EAT
    """
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        kenya_time = time_obj + timedelta(hours=3)
        return kenya_time.strftime('%H:%M')
    except:
        return time_str


def fetch_mozzartbet_matches(headless=True):
    """
    Fetch football matches from MozzartBet with KENYA TIMEZONE
    """

    print("=" * 70)
    print("⚽ FETCHING MOZZARTBET KENYA FOOTBALL MATCHES")
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
        football_url = "https://www.mozzartbet.co.ke/en#/betting/?sid=1"
        print(f"\n📡 Loading MozzartBet football page...")
        driver.get(football_url)
        time.sleep(8)

        # Handle popup
        try:
            cancel_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
            cancel_btn.click()
            print("✅ Closed notification popup")
            time.sleep(2)
        except:
            pass

        # Scroll to load matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get all text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = page_text.split('\n')

        print(f"\n📦 Scanning for match containers...")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for date+time pattern with match ID (e.g., "Thu 23:00|11722")
            match_header = re.search(r'([A-Za-z]+ \d{2}:\d{2})\|(\d+)', line)

            if match_header:
                datetime_str = match_header.group(1)
                match_id = match_header.group(2)

                # Extract time
                time_match = re.search(r'(\d{2}:\d{2})', datetime_str)
                gmt_time = time_match.group(1) if time_match else "00:00"

                # CONVERT TO KENYA TIME
                kenya_time = convert_to_kenya_time(gmt_time)

                # Get today's date in DD/MM format
                today = datetime.now().strftime('%d/%m')

                # League is usually in the previous line
                league = "Football"
                if i > 0 and lines[i - 1].strip():
                    league = lines[i - 1].strip()
                    # Clean up league name (capitalize properly)
                    league = league.title()

                # Teams are in the next 2 lines
                home = "Unknown"
                away = "Unknown"

                if i + 1 < len(lines):
                    home = lines[i + 1].strip()
                if i + 2 < len(lines):
                    away = lines[i + 2].strip()

                # Validate we have real team names
                if home and away and home != away and len(home) > 2 and len(away) > 2:
                    # Clean team names
                    home = home.strip()
                    away = away.strip()

                    match = {
                        'home': home,
                        'away': away,
                        'kickoff': kenya_time,  # KENYA TIME
                        'date': today,
                        'league': league,
                        'bookie': 'MozzartBet'
                    }
                    matches.append(match)

                    # Print in Odibets style with fixed width columns
                    print(f"✅ {home:30} vs {away:30} @ {kenya_time} [{today}]")

                    # Skip ahead past the odds
                    i += 5
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
    filename = f"mozzartbet_matches_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")

    csv_filename = filename.replace('.json', '.csv')
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Home Team,Away Team,Kickoff (EAT),Date,League,Bookie\n")
        for match in matches:
            f.write(
                f"{match['home']},{match['away']},{match['kickoff']},{match['date']},\"{match['league']}\",{match['bookie']}\n")
    print(f"💾 Saved {len(matches)} matches to {csv_filename}")


def quick_test():
    """Quick test function"""
    print("🔧 TESTING MOZZARTBET FOOTBALL SCRAPER")
    print("-" * 50)

    matches = fetch_mozzartbet_matches(headless=False)

    if matches:
        print(f"\n✅ MozzartBet: {len(matches)} valid matches with kickoff times")
        save_matches(matches)
    else:
        print("\n❌ No matches found")


if __name__ == "__main__":
    quick_test()