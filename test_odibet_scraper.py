# odibets_scraper_working.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import re
import json


def fetch_odibets_matches(headless=True):
    """
    Fetch football matches from Odibets - WORKING VERSION
    Based on the actual HTML structure with a.t elements
    """

    print("=" * 70)
    print("⚽ FETCHING ODIBETS MATCHES")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        print("\n📡 Loading Odibets soccer page...")
        driver.get("https://www.odibets.com/sports/soccer")
        time.sleep(5)

        # Close popup if exists
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
            driver.execute_script("arguments[0].click();", close_btn)
            print("✅ Popup closed")
            time.sleep(2)
        except:
            pass

        # Find all match containers (a tags with class "t")
        match_containers = driver.find_elements(By.CSS_SELECTOR, "a.t")
        print(f"📦 Found {len(match_containers)} match containers")

        for container in match_containers:
            try:
                # Get all divs with class "t-l" (team names)
                team_divs = container.find_elements(By.CSS_SELECTOR, "div.t-l")

                if len(team_divs) >= 2:
                    home = team_divs[0].text.strip()
                    away = team_divs[1].text.strip()

                    # Find time element (inside t-m div with font-bold span)
                    try:
                        time_element = container.find_element(By.CSS_SELECTOR, "div.t-m span.font-bold")
                        time_text = time_element.text.strip()

                        # Parse date and time (format: "16/02 23:00")
                        time_match = re.search(r'(\d{2}/\d{2})\s+(\d{2}:\d{2})', time_text)
                        if time_match:
                            date = time_match.group(1)
                            kickoff = time_match.group(2)

                            match = {
                                'home': home,
                                'away': away,
                                'kickoff': kickoff,
                                'date': date,
                                'league': 'Football',  # League info might be elsewhere
                                'bookie': 'Odibets',
                                'datetime': f"{datetime.now().year}-{date.replace('/', '-')} {kickoff}"
                            }
                            matches.append(match)
                            print(f"✅ {home:30} vs {away:30} @ {kickoff} [{date}]")
                    except:
                        continue

            except Exception as e:
                continue

        print(f"\n📊 Total matches found: {len(matches)}")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

    finally:
        driver.quit()


def save_matches(matches):
    """Save matches to JSON file"""
    if not matches:
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"odibets_matches_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")


def test_odibets():
    """Test the working Odibets scraper"""

    print("\n🔧 TESTING ODIBETS SCRAPER")
    print("=" * 60)

    matches = fetch_odibets_matches(headless=False)  # Set to False to watch it work

    if matches:
        print(f"\n✅ SUCCESS! Found {len(matches)} matches")
        print("\n📋 First 10 matches:")
        for i, match in enumerate(matches[:10]):
            print(f"{i + 1:2}. {match['home']} vs {match['away']} @ {match['kickoff']} ({match['date']})")

        save_matches(matches)
    else:
        print("\n❌ No matches found")


if __name__ == "__main__":
    test_odibets()