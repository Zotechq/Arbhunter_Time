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


def display_profitable_opportunities(discrepancies, all_bookmakers=['Odibets', 'Betika', 'SportPesa']):
    """Display discrepancies using Xscores as the reference for correct time"""
    if not discrepancies:
        print("\n✅ No discrepancies found.")
        return

    # Filter to only show matches where Xscores has a time
    xscores_discrepancies = []
    for d in discrepancies:
        if 'Xscores' in d.get('all_times', {}):
            xscores_discrepancies.append(d)

    if not xscores_discrepancies:
        print("\n✅ No Xscores discrepancies found.")
        return

    print("\n" + "=" * 120)
    print(f"📊 DISCREPANCIES VS XSCORES: {len(xscores_discrepancies)}")
    print("=" * 120)

    table_data = []
    for i, d in enumerate(xscores_discrepancies, 1):
        # Get Xscores time as the reference
        all_times = d.get('all_times', {})
        xscores_time = all_times.get('Xscores', 'Unknown')

        # Create a row for each match
        row = [
            i,
            d['match'][:35] + "..." if len(d['match']) > 35 else d['match'],
            f"✅ {xscores_time}",  # Xscores is always correct
        ]

        # Add each betting site's time with comparison to Xscores
        for bookie in all_bookmakers:
            if bookie in all_times:
                time = all_times[bookie]
                # Calculate gap from Xscores
                from datetime import datetime
                try:
                    xscores_dt = datetime.strptime(xscores_time, '%H:%M')
                    bookie_dt = datetime.strptime(time, '%H:%M')
                    gap = abs((bookie_dt - xscores_dt).total_seconds() / 60)

                    if gap > 0:
                        row.append(f"❌ {time} ({gap:.0f}min)")
                    else:
                        row.append(f"✅ {time}")
                except:
                    row.append(f"❓ {time}")
            else:
                row.append("⚪ -")

        table_data.append(row)

    headers = ["#", "Match", "Xscores", "Odibets", "Betika", "SportPesa"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("=" * 120)


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