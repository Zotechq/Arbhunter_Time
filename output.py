# output.py
from tabulate import tabulate
import csv


def display_matches(matches):
    """Display matches in a table"""
    if not matches:
        print("No matches to display.")
        return
    table_data = [[m['home'], m['away'], m['league'], m['kickoff'], m['status']] for m in matches]
    print(tabulate(table_data, headers=["Home", "Away", "League", "Time", "Status"], tablefmt="pipe"))


def display_time_variations(variations):
    """Display time variations showing all bookmakers"""
    if not variations:
        print("\n✅ No time variations detected.")
        return

    print("\n" + "=" * 100)
    print(f"⚠️  TIME VARIATIONS DETECTED: {len(variations)} matches with conflicting kickoff times")
    print("=" * 100)

    table_data = []
    for i, v in enumerate(variations, 1):
        # For each variation, show both bookmakers
        outlier_bookie = v['outlier_bookies'][0]
        majority_time = v['majority_time']
        gap = v['variation_gap_minutes']

        # Determine which bookie has which time
        if outlier_bookie == "Xscores":
            odibets_time = majority_time
            xscores_time = f"🔴 {gap}min diff"
        else:
            odibets_time = "🔴 Different"
            xscores_time = majority_time

        table_data.append([
            i,
            f"{v['home']} vs {v['away']}",
            v['league'],
            f"Odibets: {odibets_time}",
            f"Xscores: {xscores_time}",
            f"{gap} min"
        ])

    headers = ["#", "Match", "League", "Odibets", "Xscores", "Gap"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Add summary
    print("\n" + "=" * 100)
    print("📌 SUMMARY:")
    for v in variations:
        outlier = v['outlier_bookies'][0]
        other = "Odibets" if outlier == "Xscores" else "Xscores"
        print(f"   • {v['home']} vs {v['away']}: {other} says {v['majority_time']}, "
              f"{outlier} is {v['variation_gap_minutes']}min different")
    print("=" * 100)


def display_profitable_opportunities(opportunities):
    """Super simple display - just the facts you need"""
    if not opportunities:
        print("\n💰 No opportunities right now.")
        return

    print("\n" + "=" * 100)
    print(f"💰 TIME DISCREPANCIES FOUND: {len(opportunities)}")
    print("=" * 100)

    table_data = []
    for i, opp in enumerate(opportunities, 1):
        # Determine which site is wrong
        wrong_site = opp['behind_bookie']
        wrong_time = opp['behind_time']
        correct_site = opp['correct_bookies'][0] if isinstance(opp['correct_bookies'], list) else opp['correct_bookies']
        correct_time = opp['correct_time']

        # Shorten long match names
        match_name = opp['match']
        if len(match_name) > 30:
            match_name = match_name[:27] + "..."

        table_data.append([
            i,
            match_name,
            f"{wrong_site} says {wrong_time}",
            f"{correct_site} says {correct_time}",
            f"{opp['gap_minutes']:.0f} min"
        ])

    headers = ["#", "Match", "Wrong", "Correct", "Gap"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))
    print("=" * 100)


def log_to_csv(data, filename):
    """Log data to CSV file"""
    if not data:
        return
    fieldnames = data[0].keys()
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)