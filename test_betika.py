#!/usr/bin/env python3
"""
Test Betika scraper
Run with: python test_betika.py
"""

from network import fetch_page
from scraper import extract_betika_matches
from bs4 import BeautifulSoup
import os


def test_betika():
    print("=" * 60)
    print("TESTING BETIKA SCRAPER")
    print("=" * 60)

    # Try to fetch live page
    url = "https://www.betika.com/en-ke/s/soccer"
    print(f"\n1. Fetching {url}...")

    soup = fetch_page(url, 1, use_selenium=True)

    if not soup:
        print("❌ Failed to fetch page")
        return

    print("✅ Page fetched successfully")

    # Save HTML for debugging
    with open("betika_test_live.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    print("✅ Saved live HTML to betika_test_live.html")

    # Extract matches
    print("\n2. Extracting matches...")
    matches = extract_betika_matches(soup, "Betika")

    # Show results
    print("\n" + "=" * 60)
    print(f"RESULTS: Found {len(matches)} Betika matches")
    print("=" * 60)

    if matches:
        print("\n📋 All matches:")
        for i, match in enumerate(matches, 1):
            # Handle None values in odds
            odds_1 = f"{match['odds_1']:.3f}" if match['odds_1'] else "N/A"
            odds_x = f"{match['odds_x']:.3f}" if match['odds_x'] else "N/A"
            odds_2 = f"{match['odds_2']:.3f}" if match['odds_2'] else "N/A"

            print(
                f"{i:2}. {match['home'][:25]:25} vs {match['away'][:25]:25} @ {match['kickoff']:5} - {odds_1}/{odds_x}/{odds_2}")
    else:
        print("\n❌ No matches found")

        # Debug: Show what's on the page
        print("\n3. Debugging page content...")

        # Look for common patterns
        all_text = soup.get_text()
        print(f"Page text length: {len(all_text)} characters")

        # Check if any team names appear
        test_teams = ['Real Madrid', 'Barcelona', 'Manchester', 'Liverpool', 'Bayern']
        print("\nSearching for team names in page:")
        for team in test_teams:
            if team.lower() in all_text.lower():
                print(f"  ✅ Found '{team}'")
            else:
                print(f"  ❌ No '{team}' found")

        # Check for time patterns
        import re
        times = re.findall(r'\d{2}:\d{2}', all_text)
        print(f"\nFound {len(times)} time patterns: {times[:10]}")


if __name__ == "__main__":
    test_betika()