# main.py
import time
from datetime import datetime, timedelta
import json
import os

# Import your scrapers
from flashscore_scraper import get_flashscore_matches
from odibets_scraper import fetch_odibets_matches
from mozzart_scraper import fetch_mozzartbet_matches
from betika_scraper import fetch_betika_matches

# Import the dynamic scheduler
from scheduler import DynamicScheduler

# Import Telegram alert
from telegram_alert import TelegramAlert


def safe_get_matches(scraper_func, source_name, scheduler=None, match_data=None):
    """
    Safely fetch matches and ensure they have the required fields
    Now with scheduler integration for failure tracking
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
            if scheduler:
                scheduler.record_failure(source_name)
            return []

        if not isinstance(matches, list):
            print(f"⚠️ {source_name} returned {type(matches)}, expected list")
            if scheduler:
                scheduler.record_failure(source_name)
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

        # Record success if we got valid matches
        if scheduler and valid_matches:
            scheduler.record_success(source_name)

        print(f"✅ {source_name}: {len(valid_matches)} valid matches with kickoff times")
        return valid_matches

    except TypeError as e:
        print(f"❌ TypeError in {source_name}: {e}")
        print(f"   This usually means you're trying to call a list as a function")
        if scheduler:
            scheduler.record_failure(source_name)
        return []
    except Exception as e:
        print(f"❌ Error fetching from {source_name}: {e}")
        if scheduler:
            scheduler.record_failure(source_name)
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


def compare_all_sources(flashscore_matches, odibets_matches, mozzartbet_matches, betika_matches):
    """
    Compare kickoff times across all FOUR sources
    Returns list of discrepancies
    """
    print("\n" + "=" * 80)
    print("🔍 COMPARING KICKOFF TIMES ACROSS ALL SOURCES")
    print("=" * 80)

    # Get today's and tomorrow's dates
    today = datetime.now().strftime('%d/%m')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m')

    print(f"\n📅 Today's date: {today}")
    print(f"📅 Tomorrow's date: {tomorrow}")

    # Flashscore web scraper shows today's matches (already in Kenya time)
    flashscore_today = [m for m in flashscore_matches if m.get('date') == today]
    flashscore_tomorrow = [m for m in flashscore_matches if m.get('date') == tomorrow]

    print(f"\n📊 Flashscore: {len(flashscore_today)} today, {len(flashscore_tomorrow)} tomorrow")
    print(f"📊 Odibets: {len(odibets_matches)} matches")
    print(f"📊 MozzartBet: {len(mozzartbet_matches)} matches")
    print(f"📊 Betika: {len(betika_matches)} matches")

    # Create lookup dictionaries
    flashscore_dict = {normalize_match_key(m['home'], m['away']): m for m in flashscore_matches}
    odibets_dict = {normalize_match_key(m['home'], m['away']): m for m in odibets_matches}
    mozzartbet_dict = {normalize_match_key(m['home'], m['away']): m for m in mozzartbet_matches}
    betika_dict = {normalize_match_key(m['home'], m['away']): m for m in betika_matches}

    # Get all unique match keys
    all_keys = set(flashscore_dict.keys()) | set(odibets_dict.keys()) | set(mozzartbet_dict.keys()) | set(
        betika_dict.keys())

    print(f"\n📊 Total unique matches found across all sources: {len(all_keys)}")

    all_discrepancies = []

    for key in all_keys:
        match_info = {}
        times = {}

        if key in flashscore_dict:
            match_info['flashscore'] = flashscore_dict[key]
            times['Flashscore'] = flashscore_dict[key]['kickoff']
        if key in odibets_dict:
            match_info['odibets'] = odibets_dict[key]
            times['Odibets'] = odibets_dict[key]['kickoff']
        if key in mozzartbet_dict:
            match_info['mozzartbet'] = mozzartbet_dict[key]
            times['MozzartBet'] = mozzartbet_dict[key]['kickoff']
        if key in betika_dict:
            match_info['betika'] = betika_dict[key]
            times['Betika'] = betika_dict[key]['kickoff']

        # If match appears in at least 2 sources, check for conflicts
        if len(times) >= 2:
            # Get the first match for display info
            sample_match = next(iter(match_info.values()))

            # Check if all times are the same
            unique_times = set(times.values())

            if len(unique_times) > 1:
                # Create unique conflict ID to prevent duplicate alerts
                conflict_id = f"{key}_{list(times.values())[0]}"

                # Conflict found!
                discrepancy = {
                    'home': sample_match['home'],
                    'away': sample_match['away'],
                    'times': times,
                    'league': sample_match.get('league', 'Unknown'),
                    'date': sample_match.get('date', 'Unknown'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'conflict_id': conflict_id
                }
                all_discrepancies.append(discrepancy)

                # Print immediately when found
                print("\n" + "!" * 70)
                print("🚨 CONFLICT FOUND!")
                print("!" * 70)
                print(f"Match: {sample_match['home']} vs {sample_match['away']}")
                print(f"League: {sample_match.get('league', 'Unknown')}")
                print(f"Date: {sample_match.get('date', 'Unknown')}")
                for source, time in times.items():
                    print(f"   {source}: {time}")

                # Calculate and show time differences
                time_values = list(times.values())
                if len(time_values) == 2:
                    diff = calculate_time_difference(time_values[0], time_values[1])
                    print(f"   Difference: {diff} minutes")
                print("!" * 70)

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
        print(f"📝 Updated running log: {log_filename}")
    except Exception as e:
        print(f"⚠️ Could not update log: {e}")


def print_summary(flashscore_count, odibets_count, mozzartbet_count, betika_count, discrepancies):
    """Print summary of current run with all FOUR sources"""
    print("\n" + "=" * 80)
    print("📊 RUN SUMMARY")
    print("=" * 80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Flashscore matches: {flashscore_count}")
    print(f"📈 Odibets matches: {odibets_count}")
    print(f"📈 MozzartBet matches: {mozzartbet_count}")
    print(f"📈 Betika matches: {betika_count}")
    print(f"📈 TOTAL matches: {flashscore_count + odibets_count + mozzartbet_count + betika_count}")
    print(f"🚨 Conflicts found: {len(discrepancies)}")

    if discrepancies:
        print("\n❌ CONFLICTS DETECTED!")
        for i, d in enumerate(discrepancies, 1):
            print(f"\n   {i}. {d['home']} vs {d['away']}")
            print(f"      League: {d.get('league', 'Unknown')}")
            print(f"      Date: {d.get('date', 'Unknown')}")
            for source, time in d['times'].items():
                print(f"      {source}: {time}")
    else:
        print("\n✅ All kickoff times match across all sources!")
    print("=" * 80)


def send_desktop_alert(discrepancies):
    """Send desktop notification for conflicts"""
    if not discrepancies:
        return

    try:
        for d in discrepancies[:3]:
            times_str = ' vs '.join([f"{s}:{t}" for s, t in d['times'].items()])
            os.system(f'notify-send "🚨 Time Conflict" "{d["home"]} vs {d["away"]}: {times_str}"')
    except:
        pass


def main_loop():
    """
    Main loop that runs with dynamic scheduling and Telegram alerts
    """
    print("=" * 80)
    print("⚽ KICKOFF TIME COMPARISON MONITOR - 4 SOURCES (DYNAMIC + TELEGRAM)")
    print("=" * 80)

    # Initialize the dynamic scheduler
    scheduler = DynamicScheduler()

    # Initialize Telegram alert
    telegram_alert = TelegramAlert()

    # Track conflicts we've already alerted on Telegram
    alerted_conflicts = set()

    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    run_count = 0

    while True:
        run_count += 1
        print(f"\n{'#' * 60}")
        print(f"🔄 RUN #{run_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#' * 60}")

        try:
            # Safely fetch matches from all FOUR sources with scheduler tracking
            flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore", scheduler)
            odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets", scheduler)
            mozzartbet_matches = safe_get_matches(fetch_mozzartbet_matches, "MozzartBet", scheduler)
            betika_matches = safe_get_matches(fetch_betika_matches, "Betika", scheduler)

            # Compare them
            discrepancies = compare_all_sources(flashscore_matches, odibets_matches, mozzartbet_matches, betika_matches)

            # Send Telegram alerts for NEW conflicts only
            for conflict in discrepancies:
                conflict_id = conflict.get('conflict_id')

                if conflict_id and conflict_id not in alerted_conflicts:
                    # Send Telegram alert
                    if telegram_alert.send_alert(conflict):
                        alerted_conflicts.add(conflict_id)
                        print(f"📱 Telegram alert sent for {conflict['home']} vs {conflict['away']}")

            # Send desktop notifications
            if discrepancies:
                send_desktop_alert(discrepancies)

            # Print summary
            print_summary(
                len(flashscore_matches),
                len(odibets_matches),
                len(mozzartbet_matches),
                len(betika_matches),
                discrepancies
            )

            # Save conflicts (all of them, not just new ones)
            if discrepancies:
                save_discrepancies(discrepancies)

            # Calculate dynamic next run time based on matches
            all_matches = flashscore_matches + odibets_matches + mozzartbet_matches + betika_matches
            if all_matches:
                # Find the match that needs scraping soonest
                soonest_interval = float('inf')

                for match in all_matches:
                    match_key = scheduler.generate_match_key(
                        match['home'],
                        match['away'],
                        match['date']
                    )

                    minutes_until = scheduler.parse_match_datetime(
                        match['date'],
                        match['kickoff']
                    )

                    should_scrape, next_in = scheduler.should_scrape(
                        match_key,
                        minutes_until,
                        match.get('league', 'Football'),
                        match['source']
                    )

                    if next_in < soonest_interval:
                        soonest_interval = next_in

                next_wait = max(1, min(soonest_interval, 30))  # Cap at 30 mins max
            else:
                next_wait = 20  # Fallback to 20 minutes

            next_run = datetime.now().timestamp() + (next_wait * 60)
            next_run_time = datetime.fromtimestamp(next_run)

            print(f"\n⏳ Dynamic scheduling: Next check in {next_wait:.1f} minutes")
            print(f"📅 Next run at: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

            time.sleep(next_wait * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Stopping monitor...")
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            print("⏳ Waiting 5 minutes before retry...")
            time.sleep(5 * 60)


def quick_test():
    """Run one comparison immediately"""
    print("🔧 QUICK TEST MODE - 4 SOURCES")
    print("=" * 60)

    flashscore_matches = safe_get_matches(get_flashscore_matches, "Flashscore")
    odibets_matches = safe_get_matches(fetch_odibets_matches, "Odibets")
    mozzartbet_matches = safe_get_matches(fetch_mozzartbet_matches, "MozzartBet")
    betika_matches = safe_get_matches(fetch_betika_matches, "Betika")

    discrepancies = compare_all_sources(flashscore_matches, odibets_matches, mozzartbet_matches, betika_matches)

    print_summary(
        len(flashscore_matches),
        len(odibets_matches),
        len(mozzartbet_matches),
        len(betika_matches),
        discrepancies
    )

    if discrepancies:
        save_discrepancies(discrepancies)


if __name__ == "__main__":
    print("⚽ KICKOFF TIME COMPARISON SYSTEM - 4 BOOKMAKERS")
    print("=" * 60)
    print("1. Run once (quick test)")
    print("2. Run with dynamic scheduler + Telegram alerts")
    print("3. Run every X minutes (custom interval)")

    choice = input("\nEnter choice (1, 2, or 3): ").strip()

    if choice == "1":
        quick_test()
    elif choice == "2":
        main_loop()
    elif choice == "3":
        try:
            minutes = int(input("Enter interval in minutes: "))
            # Reuse main_loop with fixed interval by modifying the function
            print("❌ Fixed interval mode not implemented with Telegram. Use option 2 for dynamic scheduling.")
        except:
            print("❌ Invalid number")
    else:
        print("❌ Invalid choice")