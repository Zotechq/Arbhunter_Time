# test_betika.py
from betika_scraper import fetch_betika_matches, display_matches, save_matches


def test_betika_scraper():
    """Test the Betika scraper thoroughly"""

    print("=" * 80)
    print("🔬 TESTING BETIKA SCRAPER")
    print("=" * 80)

    # Test 1: Can we fetch matches?
    print("\n📋 TEST 1: Fetching matches...")
    matches = fetch_betika_matches()

    if not matches:
        print("❌ FAILED: No matches returned")
        return False

    print(f"✅ PASSED: Got {len(matches)} matches")

    # Test 2: Check data structure
    print("\n📋 TEST 2: Validating data structure...")
    required_fields = ['home', 'away', 'kickoff', 'date', 'league', 'bookie']

    first_match = matches[0]
    missing_fields = []

    for field in required_fields:
        if field not in first_match:
            missing_fields.append(field)

    if missing_fields:
        print(f"❌ FAILED: Missing fields: {missing_fields}")
        return False

    print(f"✅ PASSED: All required fields present")

    # Test 3: Validate kickoff time format
    print("\n📋 TEST 3: Validating kickoff time format...")
    import re

    invalid_times = []
    for match in matches:
        if not re.match(r'^\d{2}:\d{2}$', match['kickoff']):
            invalid_times.append(f"{match['home']} vs {match['away']}: {match['kickoff']}")

    if invalid_times:
        print(f"⚠️ WARNING: {len(invalid_times)} matches have invalid time format")
        for inv in invalid_times[:3]:
            print(f"   • {inv}")
    else:
        print(f"✅ PASSED: All {len(matches)} matches have valid kickoff times (HH:MM)")

    # Test 4: Check for empty team names
    print("\n📋 TEST 4: Checking team names...")
    empty_teams = []
    for match in matches:
        if not match['home'] or not match['away']:
            empty_teams.append(match)

    if empty_teams:
        print(f"❌ FAILED: {len(empty_teams)} matches have empty team names")
        return False

    print(f"✅ PASSED: All team names are non-empty")

    # Test 5: Display sample matches
    print("\n📋 TEST 5: Sample matches (first 5):")
    for i, match in enumerate(matches[:5]):
        print(f"   {i + 1}. {match['home']} vs {match['away']} @ {match['kickoff']}")
        print(f"      League: {match['league']}")

    # Test 6: Save to files
    print("\n📋 TEST 6: Saving to files...")
    try:
        save_matches(matches, 'json')
        save_matches(matches, 'csv')
        print("✅ PASSED: Files saved successfully")
    except Exception as e:
        print(f"❌ FAILED: Could not save files: {e}")
        return False

    # Summary
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print(f"📊 Summary:")
    print(f"   • Total matches: {len(matches)}")
    print(f"   • Unique leagues: {len(set(m['league'] for m in matches))}")

    # Show time distribution
    times = [m['kickoff'] for m in matches]
    from collections import Counter
    time_counts = Counter(times)
    print(f"\n⏰ Kickoff times distribution:")
    for time in sorted(time_counts.keys())[:5]:  # Show first 5
        print(f"   • {time}: {time_counts[time]} matches")

    return True


def quick_test():
    """Quick test to see if scraper works"""
    print("⚡ QUICK TEST")
    print("-" * 40)

    matches = fetch_betika_matches()

    if matches:
        print(f"\n✅ SUCCESS! Found {len(matches)} matches")
        print("\n📋 First 3 matches:")
        for match in matches[:3]:
            print(f"   • {match['home']} vs {match['away']} @ {match['kickoff']}")
        return True
    else:
        print("❌ No matches found")
        return False


if __name__ == "__main__":
    print("🔧 BETIKA SCRAPER TEST SUITE")
    print("=" * 80)
    print("1. Quick test (just fetch and show)")
    print("2. Full test (validate everything)")
    print("3. Save matches only")

    choice = input("\nEnter choice (1, 2, or 3): ").strip()

    if choice == "1":
        quick_test()
    elif choice == "2":
        test_betika_scraper()
    elif choice == "3":
        matches = fetch_betika_matches()
        if matches:
            save_matches(matches)
            print(f"\n✅ Saved {len(matches)} matches")
    else:
        print("❌ Invalid choice")