# main_comparison_fixed.py
import time
from datetime import datetime
import json
import os
from collections import defaultdict

# Import your scrapers
from flashscore_scraper import get_kickoff_times as get_flashscore_matches
from betika_scraper import fetch_betika_matches





def safe_get_matches(scraper_func, source_name):
    """
    Safely fetch matches and ensure they have the required fields
    """
    try:
        print(f"\n📡 Fetching from {source_name}...")

        # Check if scraper_func is actually callable
        if not callable(scraper_func):
            print(f"❌ ERROR: {source_name} scraper is not callable!")
            print(f"   Type: {type(scraper_func)}")
            return []

        # Call the function
        matches = scraper_func()

        # Check what we got
        if matches is None:
            print(f"⚠️ {source_name} returned None")
            return []

        if not isinstance(matches, list):
            print(f"⚠️ {source_name} returned {type(matches)}, expected list")
            return []

        # Filter out matches without kickoff times
        valid_matches = []
        for match in matches:
            if match and isinstance(match, dict):
                if 'kickoff' in match and match['kickoff']:
                    # Ensure all required fields exist
                    valid_matches.append({
                        'home': match.get('home', 'Unknown'),
                        'away': match.get('away', 'Unknown'),
                        'kickoff': match['kickoff'],
                        'league': match.get('league', 'Unknown'),
                        'source': source_name
                    })
                else:
                    print(f"⚠️ Skipping match without kickoff: {match.get('home', 'Unknown')}")

        print(f"✅ {source_name}: {len(valid_matches)} valid matches with kickoff times")
        return valid_matches

    except TypeError as e:
        print(f"❌ TypeError in {source_name}: {e}")
        print(f"   This usually means you're trying to call a list as a function")
        return []
    except Exception as e:
        print(f"❌ Error fetching from {source_name}: {e}")
        return []


def safe_get_matches(scraper_func, source_name):
    """
    Safely fetch matches and ensure they have the required fields
    """
    try:
        print(f"\n📡 Fetching from {source_name}...")
        matches = scraper_func()

        # Filter out matches without kickoff times
        valid_matches = []
        for match in matches:
            if match and 'kickoff' in match and match['kickoff']:
                # Ensure all required fields exist
                valid_matches.append({
                    'home': match.get('home', 'Unknown'),
                    'away': match.get('away', 'Unknown'),
                    'kickoff': match['kickoff'],
                    'league': match.get('league', 'Unknown'),
                    'source': source_name
                })
            else:
                print(
                    f"⚠️ Skipping match without kickoff time: {match.get('home', 'Unknown')} vs {match.get('away', 'Unknown')}")

        print(f"✅ {source_name}: {len(valid_matches)} valid matches with kickoff times")
        return valid_matches

    except Exception as e:
        print(f"❌ Error fetching from {source_name}: {e}")
        return []


def normalize_team_name(name):
    """
    Normalize team name for matching across different websites
    """
    import re

    if not name:
        return ""

    # Convert to lowercase
    name = name.lower()

    # Remove common suffixes
    name = re.sub(r'\s+fc$|\s+f\.c\.$|\s+united$|\s+utd$|\s+city$', '', name)

    # Remove special characters
    name = re.sub(r'[^\w\s]', '', name)

    # Remove extra spaces
    name = ' '.join(name.split())

    return name


def normalize_match_key(home, away):
    """
    Create a normalized key to match same teams across different websites
    """
    home_norm = normalize_team_name(home)
    away_norm = normalize_team_name(away)

    # Sort teams alphabetically to handle home/away mismatches
    teams = sorted([home_norm, away_norm])
    return f"{teams[0]}-{teams[1]}"


def calculate_time_difference(time1, time2):
    """Calculate minutes difference between two times"""
    try:
        t1 = datetime.strptime(time1, '%H:%M')
        t2 = datetime.strptime(time2, '%H:%M')

        diff_minutes = abs((t1 - t2).total_seconds() / 60)
        return int(diff_minutes)
    except:
        return 999  # Return large number if time parsing fails


def compare_kickoff_times(flashscore_matches, betika_matches):
    """
    Compare kickoff times from both websites for the same matches
    """
    print("\n" + "=" * 80)
    print("🔍 COMPARING KICKOFF TIMES")
    print("=" * 80)

    discrepancies = []

    if not flashscore_matches or not betika_matches:
        print("⚠️ Not enough data to compare")
        return discrepancies

    # Create lookup dictionary for Flashscore matches
    flashscore_dict = {}
    for match in flashscore_matches:
        key = normalize_match_key(match['home'], match['away'])
        flashscore_dict[key] = match

    print(f"\n📊 Flashscore: {len(flashscore_dict)} unique matches")
    print(f"📊 Betika: {len(betika_matches)} matches")

    # Compare each Betika match with Flashscore
    matches_checked = 0

    for betika_match in betika_matches:
        key = normalize_match_key(betika_match['home'], betika_match['away'])

        if key in flashscore_dict:
            matches_checked += 1
            flashscore_match = flashscore_dict[key]

            if flashscore_match['kickoff'] != betika_match['kickoff']:
                discrepancy = {
                    'home': betika_match['home'],
                    'away': betika_match['away'],
                    'flashscore_time': flashscore_match['kickoff'],
                    'betika_time': betika_match['kickoff'],
                    'league': betika_match.get('league', 'Unknown'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time_difference': calculate_time_difference(
                        flashscore_match['kickoff'],
                        betika_match['kickoff']
                    )
                }
                discrepancies.append(discrepancy)

                # Print immediately when found
                print("\n" + "!" * 60)
                print("🚨 CONFLICT FOUND!")
                print("!" * 60)
                print(f"Match: {betika_match['home']} vs {betika_match['away']}")
                print(f"League: {betika_match.get('league', 'Unknown')}")
                print(f"Flashscore says: {flashscore_match['kickoff']}")
                print(f"Betika says: {betika_match['kickoff']}")
                print(f"Difference: {discrepancy['time_difference']} minutes")
                print("!" * 60)

    print(f"\n📊 Matches compared: {matches_checked}")
    return discrepancies


def save_discrepancies(discrepancies):
    """Save conflicts to file"""
    if not discrepancies:
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"discrepancies_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(discrepancies, f, indent=2)

    print(f"\n💾 Saved {len(discrepancies)} conflicts to {filename}")

    # Also append to running log
    log_filename = "discrepancy_log.json"
    try:
        if os.path.exists(log_filename):
            with open(log_filename, 'r') as f:
                log = json.load(f)
        else:
            log = []

        log.extend(discrepancies)

        with open(log_filename, 'w') as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not update log: {e}")


def print_summary(flashscore_count, betika_count, discrepancies):
    """Print summary of current run"""
    print("\n" + "=" * 80)
    print("📊 RUN SUMMARY")
    print("=" * 80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Flashscore matches (with times): {flashscore_count}")
    print(f"📈 Betika matches (with times): {betika_count}")
    print(f"🚨 Conflicts found: {len(discrepancies)}")

    if discrepancies:
        print("\n❌ CONFLICTS DETECTED!")
        for d in discrepancies:
            print(f"   • {d['home']} vs {d['away']}:")
            print(
                f"     Flashscore {d['flashscore_time']} vs Betika {d['betika_time']} (diff: {d['time_difference']}min)")
    else:
        print("\n✅ All kickoff times match!")
    print("=" * 80)


def send_alert(discrepancies):
    """Send desktop notification for conflicts"""
    if not discrepancies:
        return

    try:
        for d in discrepancies[:3]:
            os.system(
                f'notify-send "🚨 Time Conflict" "{d["home"]} vs {d["away"]}: {d["flashscore_time"]} vs {d["betika_time"]}"')
    except:
        pass


def main_loop(interval_minutes=20):
    """
    Main loop that runs every X minutes
    """
    print("=" * 80)
    print("⚽ KICKOFF TIME COMPARISON MONITOR")
    print("=" * 80)
    print(f"🕒 Checking every {interval_minutes} minutes")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    run_count = 0

    while True:
        run_count += 1
        print(f"\n{'#' * 60}")
        print(f"🔄 RUN #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#' * 60}")

        try:
            # Safely fetch matches from both sources
            flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore")
            betika_matches = safe_get_matches(fetch_betika_matches, "Betika")

            # Compare them
            discrepancies = compare_kickoff_times(flashscore_matches, betika_matches)

            # Print summary
            print_summary(
                len(flashscore_matches),
                len(betika_matches),
                discrepancies
            )

            # Save conflicts
            if discrepancies:
                save_discrepancies(discrepancies)
                send_alert(discrepancies)

            # Wait for next run
            next_run = datetime.now().timestamp() + (interval_minutes * 60)
            next_run_time = datetime.fromtimestamp(next_run)

            print(f"\n⏳ Waiting {interval_minutes} minutes until next run...")
            print(f"📅 Next run at: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

            time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Stopping monitor...")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            print("⏳ Waiting 5 minutes before retry...")
            time.sleep(5 * 60)


def quick_test():
    """Run one comparison immediately"""
    print("🔧 QUICK TEST MODE")
    print("=" * 60)

    flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore")
    betika_matches = safe_get_matches(fetch_betika_matches(), "Betika")

    discrepancies = compare_kickoff_times(flashscore_matches, betika_matches)

    print_summary(
        len(flashscore_matches),
        len(betika_matches),
        discrepancies
    )

    if discrepancies:
        save_discrepancies(discrepancies)


if __name__ == "__main__":
    print("⚽ KICKOFF TIME COMPARISON SYSTEM")
    print("=" * 60)
    print("1. Run once (quick test)")
    print("2. Run every 20 minutes (monitor mode)")
    print("3. Run every X minutes (custom interval)")

    choice = input("\nEnter choice (1, 2, or 3): ").strip()

    if choice == "1":
        quick_test()
    elif choice == "2":
        main_loop(20)
    elif choice == "3":
        try:
            minutes = int(input("Enter interval in minutes: "))
            main_loop(minutes)
        except:
            print("❌ Invalid number")
    else:
        print("❌ Invalid choice")