# Test the extractor directly
from network import fetch_page
from scraper import extract_matches

soup = fetch_page("https://www.odibets.com/sports/soccer", 1, use_selenium=True)
if soup:
    matches = extract_matches(soup, "Odibets")
    print(f"\n✅ Successfully extracted {len(matches)} matches!")
    for m in matches[:3]:
        print(f"  {m['home']} vs {m['away']} - {m['kickoff']} - {m['odds_1']}/{m['odds_2']}")