from bs4 import BeautifulSoup
import re

with open("odibets_debug.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# 1. Find ALL divs that contain both a time AND team names
print("=" * 60)
print("SEARCHING FOR MATCH CONTAINERS")
print("=" * 60)

# Find all spans with times (font-bold)
time_spans = soup.find_all("span", class_="font-bold")
print(f"Found {len(time_spans)} time spans")

for i, time_span in enumerate(time_spans[:5]):  # Check first 5
    print(f"\n--- Time Span {i + 1} ---")
    print(f"Time: {time_span.text.strip()}")

    # Go up to parent to find container
    parent = time_span.parent
    print(f"Direct parent tag: {parent.name}")
    print(f"Parent classes: {parent.get('class')}")

    # Go up 2 levels
    grandparent = parent.parent
    print(f"Grandparent tag: {grandparent.name}")
    print(f"Grandparent classes: {grandparent.get('class')}")

    # Look for team names in the same container
    container = grandparent
    strong_tags = container.find_all("strong")
    if strong_tags:
        print(f"Found {len(strong_tags)} strong tags in container:")
        for strong in strong_tags[:2]:
            print(f"  - {strong.text.strip()}")

# 2. Find all possible container classes by looking at common patterns
print("\n" + "=" * 60)
print("FINDING POTENTIAL CONTAINER CLASSES")
print("=" * 60)

# Look for divs that might contain matches
all_divs = soup.find_all("div")
class_counts = {}

for div in all_divs:
    classes = div.get('class', [])
    if classes:
        class_str = ' '.join(classes)
        class_counts[class_str] = class_counts.get(class_str, 0) + 1

# Show most common classes (potential match containers)
print("\nMost common div classes (potential match containers):")
sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
for class_name, count in sorted_classes[:10]:
    print(f"  {class_name}: {count} occurrences")

# 3. Try to find a complete match example
print("\n" + "=" * 60)
print("LOOKING FOR COMPLETE MATCH EXAMPLE")
print("=" * 60)

# Look for divs containing both a time span and strong tags
for div in all_divs:
    has_time = div.find("span", class_="font-bold")
    has_strong = div.find_all("strong")

    if has_time and len(has_strong) >= 2:
        print(f"\n✅ Found potential match container!")
        print(f"Div classes: {div.get('class')}")
        print(f"Time: {has_time.text.strip()}")
        for strong in has_strong[:2]:
            print(f"Team: {strong.text.strip()}")

        # Show the HTML structure
        print("\nHTML structure:")
        print(div.prettify()[:500])
        break