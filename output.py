# output.py
# New focus: Time-Discrepancy Hunting display

from tabulate import tabulate
import csv

def display_matches(matches):
    if not matches:
        print("No matches to display.")
        return
    table_data = [[m['home'], m['away'], m['league'], m['kickoff'], m['status']] for m in matches]
    print(tabulate(table_data, headers=["Home", "Away", "League", "Time", "Status"], tablefmt="pipe"))

def display_time_variations(variations):
    table_data = []
    for v in variations:
        match_str = f"{v['home']} vs {v['away']}"
        outliers_str = ', '.join(v['outlier_bookies'])
        table_data.append([
            match_str,
            v['league'],
            v['majority_time'],
            outliers_str,
            v['variation_gap_minutes']
        ])
    print(tabulate(table_data, headers=["Match", "League", "Majority Time", "Outlier Bookie(s)", "Gap (mins)"], tablefmt="pipe"))

def log_to_csv(data, filename):
    if not data:
        return
    fieldnames = data[0].keys()
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(data)