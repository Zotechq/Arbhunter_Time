from network import fetch_page
from scraper import extract_betika_matches
from bs4 import BeautifulSoup

# Load the saved HTML for testing
with open("betika_debug.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

matches = extract_betika_matches(soup, "Betika")
print(f"\n✅ Found {len(matches)} matches")

if matches:
    print("\nFirst 5 matches:")
    for i, m in enumerate(matches[:5]):
        print(f"{i+1}. {m['home']} vs {m['away']} @ {m['kickoff']} - {m['league']}")