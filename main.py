# main_comparison.py
import time
from datetime import datetime
import json
import os
from collections import defaultdict

# Import your scrapers
from flashscore_api import get_flashscore_matches  # 👈 Changed to API
from betika_scraper import fetch_betika_matches
from odibets_scraper import fetch_odibets_matches


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
                        'date': match.get('date', 'Unknown'),
                        'source': source_name
                    })
                else:
                    print(
                        f"⚠️ Skipping match without kickoff: {match.get('home', 'Unknown')} vs {match.get('away', 'Unknown')}")

        print(f"✅ {source_name}: {len(valid_matches)} valid matches with kickoff times")
        return valid_matches

    except TypeError as e:
        print(f"❌ TypeError in {source_name}: {e}")
        print(f"   This usually means you're trying to call a list as a function")
        return []
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
    name = re.sub(r'\s+fc$|\s+f\.c\.$|\s+united$|\s+utd$|\s+city$|\s+cf$|\s+f\.c\.$', '', name)

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


def compare_all_sources(flashscore_matches, betika_matches, odibets_matches):
    """
    Compare kickoff times across all three websites
    """
    print("\n" + "=" * 80)
    print("🔍 COMPARING KICKOFF TIMES ACROSS ALL SOURCES")
    print("=" * 80)

    all_discrepancies = []

    # Create dictionaries for each source
    flashscore_dict = {normalize_match_key(m['home'], m['away']): m for m in flashscore_matches}
    betika_dict = {normalize_match_key(m['home'], m['away']): m for m in betika_matches}
    odibets_dict = {normalize_match_key(m['home'], m['away']): m for m in odibets_matches}

    # Get all unique match keys
    all_keys = set(flashscore_dict.keys()) | set(betika_dict.keys()) | set(odibets_dict.keys())

    print(f"\n📊 Total unique matches found across all sources: {len(all_keys)}")

    for key in all_keys:
        match_info = {}
        times = {}

        if key in flashscore_dict:
            match_info['flashscore'] = flashscore_dict[key]
            times['Flashscore'] = flashscore_dict[key]['kickoff']
        if key in betika_dict:
            match_info['betika'] = betika_dict[key]
            times['Betika'] = betika_dict[key]['kickoff']
        if key in odibets_dict:
            match_info['odibets'] = odibets_dict[key]
            times['Odibets'] = odibets_dict[key]['kickoff']

        # If match appears in at least 2 sources, check for conflicts
        if len(times) >= 2:
            # Get the first match for display info
            sample_match = next(iter(match_info.values()))

            # Check if all times are the same
            unique_times = set(times.values())

            if len(unique_times) > 1:
                # Conflict found!
                discrepancy = {
                    'home': sample_match['home'],
                    'away': sample_match['away'],
                    'times': times,
                    'league': sample_match.get('league', 'Unknown'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                all_discrepancies.append(discrepancy)

                # Print immediately when found
                print("\n" + "!" * 70)
                print("🚨 CONFLICT FOUND!")
                print("!" * 70)
                print(f"Match: {sample_match['home']} vs {sample_match['away']}")
                print(f"League: {sample_match.get('league', 'Unknown')}")
                for source, time in times.items():
                    print(f"   {source}: {time}")
                print("!" * 70)

    return all_discrepancies


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


def print_summary(flashscore_count, betika_count, odibets_count, discrepancies):
    """Print summary of current run"""
    print("\n" + "=" * 80)
    print("📊 RUN SUMMARY")
    print("=" * 80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Flashscore matches: {flashscore_count}")
    print(f"📈 Betika matches: {betika_count}")
    print(f"📈 Odibets matches: {odibets_count}")
    print(f"📈 TOTAL matches: {flashscore_count + betika_count + odibets_count}")
    print(f"🚨 Conflicts found: {len(discrepancies)}")

    if discrepancies:
        print("\n❌ CONFLICTS DETECTED!")
        for i, d in enumerate(discrepancies, 1):
            print(f"\n   {i}. {d['home']} vs {d['away']}")
            for source, time in d['times'].items():
                print(f"      {source}: {time}")
    else:
        print("\n✅ All kickoff times match across all sources!")
    print("=" * 80)


def send_alert(discrepancies):
    """Send desktop notification for conflicts"""
    if not discrepancies:
        return

    try:
        for d in discrepancies[:3]:
            times_str = ' vs '.join([f"{s}:{t}" for s, t in d['times'].items()])
            os.system(f'notify-send "🚨 Time Conflict" "{d["home"]} vs {d["away"]}: {times_str}"')
    except:
        pass


def main_loop(interval_minutes=20):
    """
    Main loop that runs every X minutes
    """
    print("=" * 80)
    print("⚽ KICKOFF TIME COMPARISON MONITOR - 3 SOURCES")
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
            # Safely fetch matches from all three sources
            flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore (API)")
            betika_matches = safe_get_matches(fetch_betika_matches, "Betika")
            odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets")

            # Compare them
            discrepancies = compare_all_sources(flashscore_matches, betika_matches, odibets_matches)

            # Print summary
            print_summary(
                len(flashscore_matches),
                len(betika_matches),
                len(odibets_matches),
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
    print("🔧 QUICK TEST MODE - 3 SOURCES")
    print("=" * 60)

    flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore (API)")
    betika_matches = safe_get_matches(fetch_betika_matches, "Betika")
    odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets")

    discrepancies = compare_all_sources(flashscore_matches, betika_matches, odibets_matches)

    print_summary(
        len(flashscore_matches),
        len(betika_matches),
        len(odibets_matches),
        discrepancies
    )

    if discrepancies:
        save_discrepancies(discrepancies)


if __name__ == "__main__":
    print("⚽ KICKOFF TIME COMPARISON SYSTEM - 3 BOOKMAKERS")
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