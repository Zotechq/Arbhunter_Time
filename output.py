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
    """Display time variations showing Odibets, Betika, and Xscores"""
    if not variations:
        print("\n✅ No time variations detected.")
        return

    print("\n" + "=" * 120)
    print(f"⚠️  TIME VARIATIONS DETECTED: {len(variations)} matches with conflicting kickoff times")
    print("=" * 120)

    table_data = []
    for i, v in enumerate(variations, 1):
        # Initialize times
        odibets_time = "—"
        betika_time = "—"
        xscores_time = "—"

        # This is simplified - you'll need to extract actual times from your variation data
        # You may need to modify detect_variations to return all bookmaker times

        # For now, let's create a formatted display
        match_display = v['match']
        league_display = v['league']

        # Create a readable format
        gap_min = v['variation_gap_minutes']
        gap_display = f"{gap_min:.0f} min"

        # Which bookie is the outlier?
        outlier = v['outlier_bookies'][0] if v['outlier_bookies'] else "Unknown"

        # Assign times based on your data structure
        # This is a placeholder - adjust based on your actual data
        if outlier == "Xscores":
            odibets_time = v['majority_time']
            betika_time = v['majority_time']
            xscores_time = f"🔴 {gap_min}min diff"
        elif outlier == "Odibets":
            odibets_time = f"🔴 {gap_min}min diff"
            betika_time = v['majority_time']
            xscores_time = v['majority_time']
        elif outlier == "Betika":
            odibets_time = v['majority_time']
            betika_time = f"🔴 {gap_min}min diff"
            xscores_time = v['majority_time']
        else:
            odibets_time = v.get('odibets_time', '—')
            betika_time = v.get('betika_time', '—')
            xscores_time = v.get('xscores_time', '—')

        table_data.append([
            i,
            match_display,
            league_display,
            odibets_time,
            betika_time,
            xscores_time,
            gap_display
        ])

    headers = ["#", "Match", "League", "Odibets", "Betika", "Xscores", "Gap"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    print("\n" + "=" * 120)
    print("📌 SUMMARY:")
    # Group by match to avoid duplicate summaries
    seen = set()
    for v in variations:
        match_key = v['match']
        if match_key not in seen:
            outlier = v['outlier_bookies'][0] if v['outlier_bookies'] else "Unknown"
            other = "Odibets" if outlier != "Odibets" else "Betika"
            if outlier == "Odibets":
                other = "Betika/Xscores"
            elif outlier == "Betika":
                other = "Odibets/Xscores"
            elif outlier == "Xscores":
                other = "Odibets/Betika"

            print(
                f"   • {match_key}: {other} say {v['majority_time']}, {outlier} is {v['variation_gap_minutes']:.0f}min different")
            seen.add(match_key)
    print("=" * 120)


def display_profitable_opportunities(opportunities):
    """Show only the variations you can actually make money from"""
    if not opportunities:
        print("\n💰 No profitable opportunities right now.")
        return

    print("\n" + "💰" * 70)
    print(f"PROFITABLE OPPORTUNITIES FOUND: {len(opportunities)}")
    print("" * 70)

    table_data = []
    for i, opp in enumerate(opportunities, 1):
        table_data.append([
            i,
            opp['match'],
            opp['behind_bookie'],
            opp['behind_time'],
            f"{', '.join(opp['correct_bookies'])}",
            opp['correct_time'],
            f"{opp['gap_minutes']} min",
            opp['window_until'],
            opp['confidence']
        ])

    headers = ["#", "Match", "Behind Bookie", "Shows", "Correct Bookies", "Actual", "Gap", "Window Until", "Confidence"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    print("\n📌 HOW TO PROFIT:")
    for opp in opportunities[:3]:
        print(f"\n   {opp['strategy']}")

    print("\n" + "💰" * 70)

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