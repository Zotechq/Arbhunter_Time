from network import fetch_page
from scraper import extract_matches

url = "https://www.ke.sportpesa.com/en/sports-betting/football-1/"
soup = fetch_page(url, 1, use_selenium=True)

if soup:
    matches = extract_matches(soup, "SportPesa")
    print(f"\n✅ Found {len(matches)} SportPesa matches")
    for m in matches[:5]:
        print(f"  {m['home']} vs {m['away']} @ {m['kickoff']} - {m['league']}")