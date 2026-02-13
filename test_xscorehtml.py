from bs4 import BeautifulSoup
import re


def parse_xscores_html():
    with open("xscores_stealth.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    print("=" * 60)
    print("PARSING XSCORES MATCHES")
    print("=" * 60)

    # Find all match lines
    match_lines = soup.find_all("div", class_=re.compile("match_line"))
    print(f"Found {len(match_lines)} match lines\n")

    matches = []
    for i, line in enumerate(match_lines[:10]):  # First 10 matches
        print(f"--- Match {i + 1} ---")

        # Extract team names
        team_names = line.find_all("div", class_=re.compile("team_name"))
        home = away = None
        if len(team_names) >= 2:
            home = team_names[0].text.strip()
            away = team_names[1].text.strip()
            print(f"Teams: {home} vs {away}")

        # Extract scores
        scores = line.find_all("div", class_=re.compile("score"))
        if scores:
            score_text = ' '.join([s.text.strip() for s in scores if s.text.strip()])
            print(f"Scores: {score_text}")

        # Extract time/status
        time_elem = line.find("div", class_=re.compile("ko_time"))
        if time_elem:
            print(f"Time: {time_elem.text.strip()}")

        # Extract match status (live, HT, FT, etc.)
        status_elem = line.find("div", class_=re.compile("status"))
        if status_elem:
            print(f"Status: {status_elem.text.strip()}")

        print()

    # Try a more specific selector based on the sample HTML
    print("\n" + "=" * 60)
    print("DETAILED MATCH EXAMPLE")
    print("=" * 60)

    # Look for the exact structure from your output
    example = soup.find("div", class_="match_line_upper")
    if example:
        print(example.prettify()[:1000])


if __name__ == "__main__":
    parse_xscores_html()