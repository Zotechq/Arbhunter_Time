# main.py - Entry point
# New focus: Time-Discrepancy Hunting as primary output

import time
import schedule
from config import REFRESH_INTERVAL_MINUTES, BOOKMAKER_URLS, CSV_MATCHES, CSV_VARIATIONS, CSV_ARBS
from network import fetch_page
from scraper import extract_matches
from engine import detect_variations, detect_arbs  # detect_arbs deprioritized
from output import display_matches, display_time_variations, log_to_csv

request_counter = 0


def main_loop():
    global request_counter
    print(f"\n=== Time-Hunting cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    all_matches = []

    for bookie_url, bookie_name in BOOKMAKER_URLS:
        request_counter += 1
        print(f"Scraping {bookie_name} ({bookie_url})...")
        soup = fetch_page(bookie_url, request_counter)
        if soup:
            matches = extract_matches(soup, bookie_name)
            print(f"  → {len(matches)} events")
            all_matches.extend(matches)

    if not all_matches:
        print("No matches this cycle.")
        return

    display_matches(all_matches)
    log_to_csv(all_matches, CSV_MATCHES)

    variations = detect_variations(all_matches)
    if variations:
        print(f"\nTIME VARIATIONS DETECTED ({len(variations)})")
        display_time_variations(variations)
        log_to_csv(variations, CSV_VARIATIONS)

    # Deprioritized arb detection – only log, no print
    arbs = detect_arbs(all_matches)
    if arbs:
        log_to_csv(arbs, CSV_ARBS)  # Optional silent logging

    print("Cycle complete.\n")


if __name__ == "__main__":
    print("ArbHunter Time Hunter v2.0")
    print(f"Running every {REFRESH_INTERVAL_MINUTES} min.\n")
    schedule.every(REFRESH_INTERVAL_MINUTES).minutes.do(main_loop)
    main_loop()  # Initial run
    while True:
        schedule.run_pending()
        time.sleep(1)