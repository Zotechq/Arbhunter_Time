# flashscore_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import time
import re
import json
import csv


def get_kickoff_times():
    """
    Get ONLY matches with actual kickoff times from Flashscore
    """

    print("=" * 70)
    print("⏰ FETCHING MATCHES WITH KICKOFF TIMES")
    print("=" * 70)

    options = Options()
    options.add_argument("--headless")  # Run in background
    driver = webdriver.Firefox(options=options)

    matches_with_times = []

    try:
        print("\n📡 Loading Flashscore...")
        driver.get("https://www.flashscore.co.ke")
        time.sleep(8)  # Wait for page to load

        # Get all text from the page
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = page_text.split('\n')

        print("\n🔍 Extracting matches with kickoff times...")
        print("-" * 70)

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for kickoff times (e.g., "22:30", "23:30")
            if re.match(r'^\d{2}:\d{2}$', line):
                kickoff = line

                # Next line should be home team
                if i + 1 < len(lines):
                    home = lines[i + 1].strip()

                    # Next line should be away team
                    if i + 2 < len(lines):
                        away = lines[i + 2].strip()

                        # Verify these look like team names
                        if (len(home) > 2 and len(away) > 2 and
                                not home.isupper() and not away.isupper() and
                                '•' not in home and '•' not in away):
                            match = {
                                'home': home,
                                'away': away,
                                'kickoff': kickoff,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'timestamp': f"{datetime.now().strftime('%Y-%m-%d')} {kickoff}"
                            }

                            matches_with_times.append(match)
                            print(f"⏰ {home:35} vs {away:35} @ {kickoff}")

                            # Skip ahead to avoid re-processing
                            i += 3
                            continue

            i += 1

        print(f"\n📊 Found {len(matches_with_times)} matches with kickoff times")
        return matches_with_times

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

    finally:
        driver.quit()


def save_as_json(matches, filename=None):
    """Save matches to JSON file"""
    if not matches:
        return

    if not filename:
        filename = f"kickoff_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved {len(matches)} matches to {filename}")


def save_as_csv(matches, filename=None):
    """Save matches to CSV file for easy viewing in Excel"""
    if not matches:
        return

    if not filename:
        filename = f"kickoff_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Home Team', 'Away Team', 'Kickoff Time', 'Date'])
        for match in matches:
            writer.writerow([match['home'], match['away'], match['kickoff'], match['date']])

    print(f"💾 Saved {len(matches)} matches to {filename}")


def display_matches(matches):
    """Display matches in a clean table format"""
    if not matches:
        print("\n❌ No matches found")
        return

    print("\n" + "=" * 90)
    print(f"📋 MATCHES WITH KICKOFF TIMES - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 90)
    print(f"{'#':<3} {'HOME TEAM':<40} {'AWAY TEAM':<40} {'KICKOFF':<8}")
    print("-" * 90)

    # Sort by kickoff time (earliest first)
    sorted_matches = sorted(matches, key=lambda x: x['kickoff'])

    for i, match in enumerate(sorted_matches, 1):
        print(f"{i:<3} {match['home'][:39]:<40} {match['away'][:39]:<40} {match['kickoff']:<8}")

    print("=" * 90)
    print(f"Total: {len(matches)} matches")


def get_matches_for_comparison():
    """
    Returns matches in the format needed for your time comparison function
    """
    matches = get_kickoff_times()

    # Format for your compare_times function
    formatted_matches = []
    for match in matches:
        formatted_matches.append({
            'home': match['home'],
            'away': match['away'],
            'kickoff_time': match['kickoff'],
            'bookie': 'Flashscore',
            'date': match['date']
        })

    return formatted_matches


def quick_test():
    """Quick test function to see if scraper works"""
    print("🔧 TESTING FLASHSCORE SCRAPER")
    print("-" * 50)

    matches = get_kickoff_times()

    if matches:
        print(f"\n✅ SUCCESS! Found {len(matches)} matches")
        print("\n📋 First 5 matches:")
        for match in matches[:5]:
            print(f"   • {match['home']} vs {match['away']} @ {match['kickoff']}")
        return True
    else:
        print("\n❌ No matches found")
        return False


if __name__ == "__main__":
    print("⚽ FLASHSCORE MATCH SCRAPER")
    print("=" * 70)

    # Option 1: Quick test
    print("\n1. Quick test")
    print("2. Full scrape and save")
    print("3. Get matches for time comparison")

    choice = input("\nEnter choice (1, 2, or 3): ").strip()

    if choice == "1":
        quick_test()

    elif choice == "2":
        matches = get_kickoff_times()
        if matches:
            display_matches(matches)
            save_as_json(matches)
            save_as_csv(matches)

    elif choice == "3":
        comparison_matches = get_matches_for_comparison()
        if comparison_matches:
            print(f"\n✅ Ready for time comparison: {len(comparison_matches)} matches")
            print("\n📋 Sample:")
            for match in comparison_matches[:5]:
                print(f"   {match['home']} vs {match['away']} @ {match['kickoff_time']}")

    else:
        print("❌ Invalid choice")