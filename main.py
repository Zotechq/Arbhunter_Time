# main.py - Entry point
# New focus: Time-Discrepancy Hunting as primary output

import time
import schedule
from config import REFRESH_INTERVAL_MINUTES, BOOKMAKER_URLS, CSV_MATCHES, CSV_VARIATIONS, CSV_ARBS
from network import fetch_page
from scraper import extract_matches
from engine import detect_variations, detect_arbs, detect_profitable_variations  # detect_arbs deprioritized
from output import display_matches, display_time_variations, log_to_csv, display_profitable_opportunities
from engine import analyze_all_discrepancies
from output import display_profitable_opportunities

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

            print(f"\n📊 MATCH COUNT BY BOOKMAKER:")
            bookie_counts = {}
            for match in all_matches:
                bookie = match['bookie']
                bookie_counts[bookie] = bookie_counts.get(bookie, 0) + 1

            for bookie, count in bookie_counts.items():
                print(f"   • {bookie}: {count} matches")

            print("\n🔍 SportPesa matches found:")
            sportpesa_matches = [m for m in all_matches if m['bookie'] == 'SportPesa']
            for m in sportpesa_matches[:5]:  # Show first 5
                print(f"  • {m['home']} vs {m['away']} @ {m['kickoff']}")
            if len(sportpesa_matches) > 5:
                print(f"  ... and {len(sportpesa_matches) - 5} more")

            # Also show which bookmakers are missing
            all_bookies = ['Odibets', 'Betika', 'SportPesa', 'Xscores']
            for bookie in all_bookies:
                if bookie not in bookie_counts:
                    print(f"   • {bookie}: 0 matches ⚠️")
            # 👆 END OF DEBUG CODE 👆

    if not all_matches:
        print("No matches this cycle.")
        return

    #display_matches(all_matches)
    discrepancies = analyze_all_discrepancies(all_matches)
    if discrepancies:
        display_profitable_opportunities(discrepancies)
        # Optional: Save to CSV
        log_to_csv(discrepancies, "discrepancies.csv")
    #log_to_csv(all_matches, CSV_MATCHES)

    '''profitable_ops = detect_profitable_variations(all_matches)
    if profitable_ops:
        display_profitable_opportunities(profitable_ops)
        # Also log them for tracking
        log_to_csv(profitable_ops, "profitable_opportunities.csv")'''


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