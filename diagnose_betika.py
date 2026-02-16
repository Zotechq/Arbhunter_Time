# diagnose_betika.py
import inspect

print("🔍 DIAGNOSING BETIKA IMPORT")
print("=" * 50)

# Try different import methods
print("\n1. Importing directly:")
from betika_scraper import fetch_betika_matches

print(f"   Type: {type(fetch_betika_matches())}")
print(f"   Callable? {callable(fetch_betika_matches())}")
if callable(fetch_betika_matches()):
    print("   ✅ It's a function!")
else:
    print("   ❌ It's NOT a function")
    if isinstance(fetch_betika_matches, list):
        print(f"   It's a list with {len(fetch_betika_matches)} items")

print("\n2. Inspecting the module:")
import betika_scraper

print(f"   Module type: {type(betika_scraper)}")
print(f"   Functions in module: {[f for f in dir(betika_scraper) if not f.startswith('_')]}")

# Check what get_betika_matches really is
if 'get_betika_matches' in dir(betika_scraper):
    attr = getattr(betika_scraper, 'get_betika_matches')
    print(f"\n   'get_betika_matches' in module is type: {type(attr)}")

    # If it's a function, try to call it
    if callable(attr):
        print("   ✅ It's callable - trying to call it...")
        try:
            result = attr()
            print(f"   Called successfully! Got {len(result) if result else 0} matches")
        except Exception as e:
            print(f"   ❌ Error calling: {e}")
else:
    print("   ❌ 'get_betika_matches' not found in module!")

print("\n3. Checking for common naming conflicts:")
for name in dir(betika_scraper):
    if name != 'get_betika_matches' and 'betika' in name.lower():
        val = getattr(betika_scraper, name)
        print(f"   {name}: {type(val)}")