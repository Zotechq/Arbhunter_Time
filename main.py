# main_comparison.py
import time
from datetime import datetime, timedelta
import json
import os

# Import your scrapers
from flashscore_api import get_flashscore_matches
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
                    valid_matches.append({
                        'home': match.get('home', 'Unknown'),
                        'away': match.get('away', 'Unknown'),
                        'kickoff': match['kickoff'],
                        'league': match.get('league', 'Unknown'),
                        'date': match.get('date', datetime.now().strftime('%d/%m')),
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
        return 999


def compare_flashscore_odibets(flashscore_matches, odibets_matches):
    """
    Compare kickoff times between Flashscore and Odibets only
    """
    print("\n" + "=" * 80)
    print("🔍 COMPARING FLASHSCORE VS ODIBETS")
    print("=" * 80)

    # Get today's and tomorrow's dates
    today = datetime.now().strftime('%d/%m')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m')

    print(f"\n📅 Today's date: {today}")
    print(f"📅 Tomorrow's date: {tomorrow}")

    # Separate Flashscore matches by date
    flashscore_today = [m for m in flashscore_matches if m.get('date') == today]
    flashscore_tomorrow = [m for m in flashscore_matches if m.get('date') == tomorrow]

    print(f"\n📊 Flashscore: {len(flashscore_today)} today, {len(flashscore_tomorrow)} tomorrow")
    print(f"📊 Odibets: {len(odibets_matches)} matches")

    # Create lookup dictionaries
    odibets_dict = {normalize_match_key(m['home'], m['away']): m for m in odibets_matches}
    flashscore_today_dict = {normalize_match_key(m['home'], m['away']): m for m in flashscore_today}
    flashscore_tomorrow_dict = {normalize_match_key(m['home'], m['away']): m for m in flashscore_tomorrow}

    all_discrepancies = []

    # 1. Compare Flashscore (today) vs Odibets (today)
    if flashscore_today_dict:
        print("\n🔍 Comparing TODAY'S matches...")
        common_today = set(flashscore_today_dict.keys()) & set(odibets_dict.keys())

        for key in common_today:
            flash_match = flashscore_today_dict[key]
            odibets_match = odibets_dict[key]

            if flash_match['kickoff'] != odibets_match['kickoff']:
                discrepancy = {
                    'home': flash_match['home'],
                    'away': flash_match['away'],
                    'flashscore_time': flash_match['kickoff'],
                    'odibets_time': odibets_match['kickoff'],
                    'league': flash_match.get('league', 'Unknown'),
                    'date': today,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time_difference': calculate_time_difference(flash_match['kickoff'], odibets_match['kickoff'])
                }
                all_discrepancies.append(discrepancy)

                print("\n" + "!" * 60)
                print("🚨 CONFLICT FOUND (TODAY)!")
                print("!" * 60)
                print(f"Match: {flash_match['home']} vs {flash_match['away']}")
                print(f"League: {flash_match.get('league', 'Unknown')}")
                print(f"Flashscore: {flash_match['kickoff']}")
                print(f"Odibets: {odibets_match['kickoff']}")
                print(f"Difference: {discrepancy['time_difference']} minutes")
                print("!" * 60)

    # 2. Compare Flashscore (tomorrow) vs Odibets (tomorrow)
    if flashscore_tomorrow_dict:
        print("\n🔍 Comparing TOMORROW'S matches...")
        common_tomorrow = set(flashscore_tomorrow_dict.keys()) & set(odibets_dict.keys())

        for key in common_tomorrow:
            flash_match = flashscore_tomorrow_dict[key]
            odibets_match = odibets_dict[key]

            if flash_match['kickoff'] != odibets_match['kickoff']:
                discrepancy = {
                    'home': flash_match['home'],
                    'away': flash_match['away'],
                    'flashscore_time': flash_match['kickoff'],
                    'odibets_time': odibets_match['kickoff'],
                    'league': flash_match.get('league', 'Unknown'),
                    'date': tomorrow,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time_difference': calculate_time_difference(flash_match['kickoff'], odibets_match['kickoff'])
                }
                all_discrepancies.append(discrepancy)

                print("\n" + "!" * 60)
                print("🚨 CONFLICT FOUND (TOMORROW)!")
                print("!" * 60)
                print(f"Match: {flash_match['home']} vs {flash_match['away']}")
                print(f"League: {flash_match.get('league', 'Unknown')}")
                print(f"Flashscore: {flash_match['kickoff']}")
                print(f"Odibets: {odibets_match['kickoff']}")
                print(f"Difference: {discrepancy['time_difference']} minutes")
                print("!" * 60)

    print(f"\n📊 Total conflicts found: {len(all_discrepancies)}")
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


def print_summary(flashscore_count, odibets_count, discrepancies):
    """Print summary of current run"""
    print("\n" + "=" * 80)
    print("📊 RUN SUMMARY")
    print("=" * 80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Flashscore matches: {flashscore_count}")
    print(f"📈 Odibets matches: {odibets_count}")
    print(f"📈 TOTAL matches: {flashscore_count + odibets_count}")
    print(f"🚨 Conflicts found: {len(discrepancies)}")

    if discrepancies:
        print("\n❌ CONFLICTS DETECTED!")
        for i, d in enumerate(discrepancies, 1):
            print(f"\n   {i}. {d['home']} vs {d['away']}")
            print(f"      Date: {d.get('date', 'Unknown')}")
            print(f"      Flashscore: {d['flashscore_time']}")
            print(f"      Odibets: {d['odibets_time']}")
            print(f"      Difference: {d['time_difference']} minutes")
    else:
        print("\n✅ All kickoff times match between Flashscore and Odibets!")
    print("=" * 80)


def send_alert(discrepancies):
    """Send desktop notification for conflicts"""
    if not discrepancies:
        return

    try:
        for d in discrepancies[:3]:
            msg = f"{d['home']} vs {d['away']}: Flashscore {d['flashscore_time']} vs Odibets {d['odibets_time']}"
            os.system(f'notify-send "🚨 Time Conflict" "{msg}"')
    except:
        pass


def main_loop(interval_minutes=20):
    """
    Main loop that runs every X minutes
    """
    print("=" * 80)
    print("⚽ KICKOFF TIME COMPARISON MONITOR - FLASHSCORE vs ODIBETS")
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
            flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore (API)")
            odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets")

            # Compare them
            discrepancies = compare_flashscore_odibets(flashscore_matches, odibets_matches)

            # Print summary
            print_summary(
                len(flashscore_matches),
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
    print("🔧 QUICK TEST MODE - FLASHSCORE vs ODIBETS")
    print("=" * 60)

    flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore (API)")
    odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets")

    discrepancies = compare_flashscore_odibets(flashscore_matches, odibets_matches)

    print_summary(
        len(flashscore_matches),
        len(odibets_matches),
        discrepancies
    )

    if discrepancies:
        save_discrepancies(discrepancies)


if __name__ == "__main__":
    print("⚽ KICKOFF TIME COMPARISON SYSTEM - FLASHSCORE vs ODIBETS")
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