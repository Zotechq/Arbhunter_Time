#!/usr/bin/env python3
"""
Quick test for Odibets scraper
Run with: python test_odibets.py
"""

from network import fetch_page
from scraper import extract_matches
import sys
from datetime import datetime


def test_odibets():
    print("=" * 60)
    print("TESTING ODIBETS SCRAPER")
    print("=" * 60)

    # 1. Fetch the page
    print("\n1️⃣  Fetching Odibets page...")
    url = "https://www.odibets.com/sports/soccer"
    soup = fetch_page(url, 1, use_selenium=True)

    if not soup:
        print("❌ Failed to fetch page")
        return False

    print("✅ Page fetched successfully")

    # 2. Extract matches
    print("\n2️⃣  Extracting matches...")
    matches = extract_matches(soup, "Odibets")

    # 3. Display results
    print("\n" + "=" * 60)
    print(f"RESULTS: Found {len(matches)} matches")
    print("=" * 60)

    if matches:
        print("\n📋 First 5 matches:")
        print("-" * 80)
        for i, match in enumerate(matches[:5]):
            print(f"{i + 1}. {match['home']} vs {match['away']}")
            print(f"   🕒 Kickoff: {match['kickoff']}")
            print(f"   📊 Odds: {match['odds_1']} / {match['odds_x']} / {match['odds_2']}")
            print(f"   🏷️  Bookie: {match['bookie']}")
            print()

        # 4. Quick validation
        print("\n3️⃣  Validating data...")
        valid_matches = 0
        for match in matches:
            if (match['home'] and match['away'] and
                    match['odds_1'] and match['odds_2']):
                valid_matches += 1

        print(f"✅ {valid_matches}/{len(matches)} matches have complete data")

        if valid_matches > 0:
            print("\n🎉 SUCCESS! Scraper is working!")
            return True
        else:
            print("\n❌ No valid matches found")
            return False
    else:
        print("\n❌ No matches extracted")
        return False


if __name__ == "__main__":
    success = test_odibets()
    sys.exit(0 if success else 1)