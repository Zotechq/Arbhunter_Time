import time
import schedule
from config import REFRESH_INTERVAL_MINUTES, BOOKMAKER_URLS
from network import fetch_page
from scraper import extract_matches
from engine import detect_arbs, detect_variations
from output import display_matches, log_to_csv
from config import CSV_MATCHES, CSV_VARIATIONS, CSV_ARBS

# Global counter for request tracking (used for IP renewal timing)
request_counter = 0


def main_loop():
    """
    Core loop that runs on schedule:
    - Fetches data from all configured bookmakers
    - Extracts and normalizes matches
    - Detects arbitrage opportunities and time variations
    - Displays results in console
    - Logs everything to CSV files
    """
    global request_counter
    print(f"\n=== Starting scrape cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    all_matches = []

    # Fetch from each bookmaker
    for bookie_url, bookie_name in BOOKMAKER_URLS:
        request_counter += 1
        print(f"Scraping {bookie_name} ({bookie_url})...")

        soup = fetch_page(bookie_url, request_counter)
        if soup:
            matches = extract_matches(soup, bookie_name)
            print(f"  → Found {len(matches)} pre-match events")
            all_matches.extend(matches)
        else:
            print(f"  → Failed to fetch from {bookie_name}")

    if not all_matches:
        print("No matches scraped this cycle. Check URLs, Tor, or selectors.")
        return

    # Display raw matches in console
    print("\nCurrent Pre-Match Matches:")
    display_matches(all_matches)

    # Log all scraped matches
    log_to_csv(all_matches, CSV_MATCHES)

    # Detect and log time variations
    variations = detect_variations(all_matches)
    if variations:
        print(f"\nFound {len(variations)} matches with varying kickoff times")
        log_to_csv(variations, CSV_VARIATIONS)

    # Detect and log arbitrage opportunities
    arbs = detect_arbs(all_matches)
    if arbs:
        print(f"\nARBS FOUND! ({len(arbs)} opportunities)")
        for arb in arbs:
            print(f"  {arb['home']} vs {arb['away']} ({arb['league']} @ {arb['kickoff']}): "
                  f"{arb['arb_pct']}% arb")
            print(f"     Best odds → 1: {arb['best_odds']['1']} ({arb['bookies']['1']}), "
                  f"X: {arb['best_odds']['X']} ({arb['bookies']['X'] or 'N/A'}), "
                  f"2: {arb['best_odds']['2']} ({arb['bookies']['2']})")
        log_to_csv(arbs, CSV_ARBS)
    else:
        print("No arbs detected this cycle (above threshold).")

    print("Cycle complete.\n")


if __name__ == "__main__":
    print("ArbHunter Pre-Match Scraper v1.0 - Starting...")
    print(f"Scheduled to run every {REFRESH_INTERVAL_MINUTES} minutes.")
    print("Make sure Tor is running (port 9050/9051).")
    print("Press Ctrl+C to stop.\n")

    # Schedule the main loop
    schedule.every(REFRESH_INTERVAL_MINUTES).minutes.do(main_loop)

    # Run once immediately on startup (useful for testing)
    main_loop()

    # Keep the script alive
    while True:
        schedule.run_pending()
        time.sleep(1)