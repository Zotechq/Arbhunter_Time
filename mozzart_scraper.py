# mozzartbet_scraper.py - FIXED VERSION WITH TIMEZONE CONVERSION
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
    If time is 19:30 GMT, returns 22:30 EAT
    """
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        kenya_time = time_obj + timedelta(hours=3)
        return kenya_time.strftime('%H:%M')
    except:
        return time_str


def fetch_mozzartbet_matches(headless=True):
    """
    Fetch football matches with proper timezone conversion
    """

    print("=" * 70)
    print("⚽ FETCHING MOZZARTBET KENYA FOOTBALL MATCHES (FIXED)")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("browser.timezone", "Africa/Nairobi")
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        football_url = "https://www.mozzartbet.co.ke/en#/betting/?sid=1"
        print(f"\n📡 Loading football matches: {football_url}")
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

        # Find all match links
        match_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/match/']")
        print(f"\n📦 Found {len(match_links)} match links")

        for link in match_links:
            try:
                link_text = link.text
                lines = link_text.split('\n')

                if len(lines) >= 3:
                    # Extract time
                    time_line = lines[0].strip()
                    time_match = re.search(r'(\d{2}:\d{2})', time_line)

                    if time_match:
                        gmt_time = time_match.group(1)
                        # CRITICAL: Convert to Kenya time
                        kenya_time = convert_to_kenya_time(gmt_time)

                        home = lines[1].strip()
                        away = lines[2].strip()

                        # Clean team names
                        home = re.sub(r'\.$', '', home).strip()
                        away = re.sub(r'\.$', '', away).strip()

                        # Get league
                        league = "Football"
                        try:
                            parent = link.find_element(By.XPATH, "..")
                            parent_text = parent.text
                            league_match = re.search(r'[a-z]+ - [a-z\s]+', parent_text.lower())
                            if league_match:
                                league = league_match.group(0).title()
                        except:
                            pass

                        match = {
                            'home': home,
                            'away': away,
                            'kickoff': kenya_time,  # NOW CORRECT!
                            'original_gmt': gmt_time,
                            'date': datetime.now().strftime('%d/%m'),
                            'league': league,
                            'bookie': 'MozzartBet',
                            'match_url': link.get_attribute('href')
                        }
                        matches.append(match)
                        print(f"✅ {home:30} vs {away:30} @ {kenya_time} (was {gmt_time} GMT) [{league[:20]}]")

            except Exception as e:
                continue

        # Remove duplicates
        unique = []
        seen = set()
        for m in matches:
            key = f"{m['home']}-{m['away']}-{m['kickoff']}"
            if key not in seen:
                seen.add(key)
                unique.append(m)

        print(f"\n📊 Total matches found: {len(unique)}")
        return unique

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        driver.quit()


def save_matches(matches):
    """Save matches to file"""
    if not matches:
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"mozzartbet_matches_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")

    csv_filename = filename.replace('.json', '.csv')
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Home Team,Away Team,Kickoff (EAT),Original GMT,Date,League,Bookie,Match URL\n")
        for match in matches:
            f.write(
                f"{match['home']},{match['away']},{match['kickoff']},{match.get('original_gmt', '')},{match['date']},\"{match['league']}\",{match['bookie']},{match.get('match_url', '')}\n")
    print(f"💾 Saved {len(matches)} matches to {csv_filename}")


def quick_test():
    """Quick test function"""
    print("🔧 TESTING MOZZARTBET FOOTBALL SCRAPER (FIXED)")
    print("-" * 50)

    matches = fetch_mozzartbet_matches(headless=False)

    if matches:
        print(f"\n✅ Success! Found {len(matches)} matches")
        print("\n📋 First 10 matches (Kenya Time):")
        for i, m in enumerate(matches[:10], 1):
            print(f"{i:2}. {m['home'][:25]:25} vs {m['away'][:25]:25} @ {m['kickoff']} (was {m['original_gmt']} GMT)")
        save_matches(matches)
    else:
        print("\n❌ No matches found")


if __name__ == "__main__":
    quick_test()