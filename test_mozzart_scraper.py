# mozzartbet_scraper.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re
import json


def fetch_mozzartbet_matches(headless=True):
    """
    Fetch REAL football matches from MozzartBet Kenya
    Based on actual HTML structure found in analysis
    """

    print("=" * 70)
    print("⚽ FETCHING MOZZARTBET KENYA FOOTBALL MATCHES")
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
        # Direct URL to football matches
        football_url = "https://www.mozzartbet.co.ke/en#/betting/?sid=1"
        print(f"\n📡 Loading football matches: {football_url}")
        driver.get(football_url)

        # Wait for page to load
        time.sleep(8)

        # Handle notification popup (Cancel button)
        try:
            cancel_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
            cancel_btn.click()
            print("✅ Closed notification popup")
            time.sleep(2)
        except:
            pass

        # Scroll to load all matches
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Find all match links (they have the pattern /match/ in href)
        print("\n🔍 Extracting football matches...")
        print("-" * 70)

        match_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/match/']")
        print(f"📦 Found {len(match_links)} match links")

        for link in match_links:
            try:
                # Get the text from the link
                link_text = link.text
                lines = link_text.split('\n')

                # Pattern from HTML:
                # Line 0: "Mon 20:00|2171" (day time | match_id)
                # Line 1: "Coventry" (home team)
                # Line 2: "Middlesbrou." (away team)

                if len(lines) >= 3:
                    # Extract time from first line
                    time_line = lines[0].strip()
                    time_match = re.search(r'(\d{2}:\d{2})', time_line)

                    if time_match:
                        kickoff = time_match.group(1)
                        home = lines[1].strip()
                        away = lines[2].strip()

                        # Clean up team names
                        home = re.sub(r'\.$', '', home).strip()
                        away = re.sub(r'\.$', '', away).strip()

                        # Get league from nearby element (if available)
                        league = "Football"
                        try:
                            # Try to find league in parent structure
                            parent = link.find_element(By.XPATH, "..")
                            parent_text = parent.text
                            # Look for league pattern (e.g., "england - the championship")
                            league_match = re.search(r'[a-z]+ - [a-z\s]+', parent_text.lower())
                            if league_match:
                                league = league_match.group(0).title()
                        except:
                            pass

                        match = {
                            'home': home,
                            'away': away,
                            'kickoff': kickoff,
                            'date': datetime.now().strftime('%d/%m'),
                            'league': league,
                            'bookie': 'MozzartBet',
                            'match_url': link.get_attribute('href')
                        }
                        matches.append(match)
                        print(f"✅ {home:30} vs {away:30} @ {kickoff} [{league[:20]}]")

            except Exception as e:
                continue

        # Remove duplicates (sometimes same match appears multiple times)
        unique_matches = []
        seen = set()
        for match in matches:
            key = f"{match['home']}-{match['away']}-{match['kickoff']}"
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)

        print(f"\n📊 Total unique football matches found: {len(unique_matches)}")
        return unique_matches

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

    # Also save as CSV
    csv_filename = filename.replace('.json', '.csv')
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Home Team,Away Team,Kickoff,Date,League,Bookie,Match URL\n")
        for match in matches:
            f.write(
                f"{match['home']},{match['away']},{match['kickoff']},{match['date']},\"{match['league']}\",{match['bookie']},{match.get('match_url', '')}\n")
    print(f"💾 Saved {len(matches)} matches to {csv_filename}")


def quick_test():
    """Quick test function"""
    print("🔧 TESTING MOZZARTBET FOOTBALL SCRAPER")
    print("-" * 50)

    matches = fetch_mozzartbet_matches(headless=False)  # Run visible for first test

    if matches:
        print(f"\n✅ Success! Found {len(matches)} matches")
        print("\n📋 First 10 matches:")
        for i, match in enumerate(matches[:10], 1):
            print(
                f"{i:2}. {match['home'][:25]:25} vs {match['away'][:25]:25} @ {match['kickoff']} [{match['league'][:20]}]")
        save_matches(matches)
    else:
        print("\n❌ No matches found")


if __name__ == "__main__":
    quick_test()