# test_js_fix.py
from flashscore_api import get_kickoff_times
from betika_scraper import fetch_betika_matches

print("Testing Flashscore with JS wait...")
flash_matches = get_kickoff_times(headless=True)

print("\nTesting Betika with JS wait...")
betika_matches = fetch_betika_matches(headless=True)

# Look specifically for Macclesfield match
for m in flash_matches:
    if 'Macclesfield' in m['home'] or 'Macclesfield' in m['away']:
        print(f"\n🔍 FOUND: Flashscore - {m['home']} vs {m['away']} @ {m['kickoff']}")

for m in betika_matches:
    if 'Macclesfield' in m['home'] or 'Macclesfield' in m['away']:
        print(f"🔍 FOUND: Betika - {m['home']} vs {m['away']} @ {m['kickoff']}")