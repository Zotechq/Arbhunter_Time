from tabulate import tabulate
import csv

def display_matches(matches):
    """
    Prints a clean ASCII table of scraped matches to the console.
    """
    if not matches:
        print("No matches to display.")
        return

    table_data = []
    for m in matches:
        table_data.append([
            m.get('home', 'N/A'),
            m.get('away', 'N/A'),
            m.get('league', 'N/A'),
            m.get('kickoff', 'N/A'),
            m.get('status', 'N/A')
        ])

        print(tabulate(
            table_data,
            headers=["Home", "Away", "League", "Time", "Status"],
            tablefmt="pipe",
            stralign="left"
        ))

def log_to_csv(data, filename):
        """
        Appends list of dictionaries to a CSV file.
        Creates header if file is new/empty.
        """
        if not data:
            return

        fieldnames = data[0].keys()

        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Write header only if file is empty (tell() == 0)
            if f.tell() == 0:
                writer.writeheader()

            writer.writerows(data)