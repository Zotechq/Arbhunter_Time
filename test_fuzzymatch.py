#!/usr/bin/env python3
"""
Test script for fuzzy matching functions
Run with: python test_fuzzy.py
"""

from helpers import fuzzy_match, normalize_name, group_fuzzy_matches


def test_normalize():
    print("=" * 50)
    print("TESTING normalize_name")
    print("=" * 50)

    test_cases = [
        ("Man Utd", "manchester united"),
        ("Liverpool FC", "liverpool"),
        ("Arsenal", "arsenal"),
        ("Real Madrid CF", "real madrid"),
        ("AC Milan", "milan"),
        ("Man Utd FC!", "manchester united"),
        ("Chelsea FC", "chelsea"),
    ]

    for input_text, expected in test_cases:
        result = normalize_name(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text}' → '{result}' (expected '{expected}')")


def test_fuzzy():
    print("\n" + "=" * 50)
    print("TESTING fuzzy_match")
    print("=" * 50)

    test_pairs = [
        ("man utd", "manchester united", True),
        ("lfc", "liverpool", True),
        ("arsenal", "chelsea", False),
        ("real madrid", "atletico madrid", False),
        ("mci", "manchester city", True),
        ("psg", "paris saint germain", True),
        ("juventus", "juve", True),
    ]

    for str1, str2, expected in test_pairs:
        result = fuzzy_match(str1, str2)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{str1}' vs '{str2}': {result} (expected {expected})")


def test_grouping():
    print("\n" + "=" * 50)
    print("TESTING group_fuzzy_matches")
    print("=" * 50)

    team_names = [
        "man utd",
        "manchester united",
        "man united",
        "liverpool",
        "lfc",
        "arsenal",
        "ars",
        "chelsea",
        "cfc",
    ]

    groups = group_fuzzy_matches(team_names)

    print(f"Found {len(groups)} groups:")
    for group_name, members in groups.items():
        print(f"\n  Group: '{group_name}'")
        for member in members:
            print(f"    - {member}")


if __name__ == "__main__":
    test_normalize()
    test_fuzzy()
    test_grouping()