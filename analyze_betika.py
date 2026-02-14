#!/usr/bin/env python3
"""
Analyze Betika HTML structure to find the right selectors
Run with: python analyze_betika.py
"""

from network import fetch_page
from bs4 import BeautifulSoup
import re


def analyze_betika():
    print("=" * 60)
    print("ANALYZING BETIKA HTML STRUCTURE")
    print("=" * 60)

    # Fetch the page
    url = "https://www.betika.com/en-ke/s/soccer"
    print(f"\n1. Fetching {url}...")

    soup = fetch_page(url, 1, use_selenium=True)

    if not soup:
        print("❌ Failed to fetch page")
        return

    print("✅ Page fetched successfully")

    # Save full HTML for inspection
    with open("betika_full.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    print("✅ Saved full HTML to betika_full.html")

    # Look for match containers
    print("\n2. Searching for match containers...")

    # Try different selectors
    selectors = [
        "div.match",
        "div.event",
        "div.fixture",
        "div.game-card",
        "div[class*='match']",
        "div[class*='event']",
        "div[class*='fixture']",
        "div[class*='game']",
        "tr",
        "li"
    ]

    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   ✅ Found {len(elements)} elements with '{selector}'")
            if len(elements) > 0:
                print(f"      Sample: {elements[0].text[:100].strip()}")

    # Look for team names
    print("\n3. Looking for team name patterns...")
    common_teams = ["Manchester", "Liverpool", "Chelsea", "Arsenal", "Real Madrid",
                    "Barcelona", "Bayern", "Juventus", "PSG", "Bandari", "AFC Leopards"]

    for team in common_teams:
        elements = soup.find_all(string=lambda t: t and team in t)
        if elements:
            print(f"   ✅ Found '{team}' in {len(elements)} places")
            for elem in elements[:2]:
                parent = elem.parent
                print(f"      Parent tag: {parent.name}, Classes: {parent.get('class')}")
                print(f"      Nearby: {str(parent)[:150]}")

    # Look for time patterns
    print("\n4. Looking for time patterns...")
    times = soup.find_all(string=lambda t: t and re.search(r'\d{2}:\d{2}', str(t)))
    print(f"   ✅ Found {len(times)} time elements")
    if times:
        for time in times[:3]:
            parent = time.parent
            print(f"      Time: {time}, Parent: {parent.name}, Classes: {parent.get('class')}")

    # Look for odds
    print("\n5. Looking for odds patterns...")
    odds = soup.find_all(string=lambda t: t and re.search(r'\d+\.\d+', str(t)))
    print(f"   ✅ Found {len(odds)} potential odds elements")
    if odds:
        for odd in odds[:5]:
            parent = odd.parent
            print(f"      Odds: {odd}, Parent: {parent.name}, Classes: {parent.get('class')}")


if __name__ == "__main__":
    analyze_betika()