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


# ✅ THIS FUNCTION WAS MISSING - ADD IT BACK
def log_to_csv(data, filename):
    """Log data to CSV file"""
    if not data:
        return
    if not data:
        return
    fieldnames = data[0].keys()
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)