# odibets_scraper.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import re
import json


def fetch_odibets_matches(headless=True):
    """
    Fetch football matches from Odibets - HEADLESS VERSION
    Based on the actual HTML structure with a.t elements
    """

    print("=" * 70)
    print("⚽ FETCHING ODIBETS MATCHES")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

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
                                'league': 'Football',
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


def save_matches(matches, filename=None):
    """Save matches to JSON file"""
    if not matches:
        print("❌ No matches to save")
        return

    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"odibets_matches_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")

    # Also save as CSV for easy viewing
    csv_filename = filename.replace('.json', '.csv')
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write("Home Team,Away Team,Kickoff,Date,Bookie\n")
        for match in matches:
            f.write(f"{match['home']},{match['away']},{match['kickoff']},{match['date']},{match['bookie']}\n")
    print(f"💾 Saved {len(matches)} matches to {csv_filename}")


def display_matches(matches):
    """Display matches in a clean table format"""
    if not matches:
        print("\n❌ No matches to display")
        return

    print("\n" + "=" * 90)
    print(f"📋 ODIBETS MATCHES - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 90)
    print(f"{'#':<3} {'HOME TEAM':<35} {'AWAY TEAM':<35} {'KICKOFF':<8} {'DATE':<8}")
    print("-" * 90)

    # Sort by kickoff time
    sorted_matches = sorted(matches, key=lambda x: x['kickoff'])

    for i, match in enumerate(sorted_matches, 1):
        print(f"{i:<3} {match['home'][:34]:<35} {match['away'][:34]:<35} {match['kickoff']:<8} {match['date']:<8}")

    print("=" * 90)
    print(f"Total: {len(matches)} matches")


def quick_test():
    """Quick test function"""
    print("🔧 QUICK TEST - ODIBETS SCRAPER")
    print("-" * 50)

    matches = fetch_odibets_matches(headless=True)

    if matches:
        display_matches(matches)
        save_matches(matches)
        return True
    else:
        print("\n❌ No matches found")
        return False


if __name__ == "__main__":
    quick_test()