from datetime import datetime, timedelta
from helpers import normalize_name
from config import MIN_TIME_BUFFER
from network import fetch_page


def extract_matches(soup, bookie_name):
    matches = []

    # Find all match containers (a tags with class "t")
    match_containers = soup.find_all("a", class_="t")
    print(f"Found {len(match_containers)} potential matches")

    # Find all odds containers
    odds_containers = soup.find_all("div", class_="odds")
    print(f"Found {len(odds_containers)} odds containers")

    # Zip them together (assuming they're in the same order)
    for i, container in enumerate(match_containers):
        try:
            # Skip if we don't have matching odds
            if i >= len(odds_containers):
                print(f"  ⚠️ No odds for match {i + 1}")
                continue

            # 1. Get team names from div.t-l
            team_divs = container.find_all("div", class_="t-l")
            if len(team_divs) < 2:
                continue

            home = team_divs[0].text.strip()
            away = team_divs[1].text.strip()

            # Skip if no real team names
            if not home or not away or home.isdigit():
                continue

            # 2. Get time from div.t-m
            time_div = container.find("div", class_="t-m")
            if not time_div:
                continue

            time_span = time_div.find("span", class_="font-bold")
            if not time_span:
                continue

            kickoff_str = time_span.text.strip().split('#')[0]  # "13/02 23:00"

            # 3. Get odds from corresponding odds container
            odds_div = odds_containers[i]
            odds_text = odds_div.text.strip()

            # Extract 1X2 odds using regex
            import re
            # Pattern matches "1 2.85 X 3.20 2 2.65"
            pattern = r'1\s+(\d+\.\d+)\s+X\s+(\d+\.\d+)\s+2\s+(\d+\.\d+)'
            odds_match = re.search(pattern, odds_text)

            if odds_match:
                odds_1 = float(odds_match.group(1))
                odds_x = float(odds_match.group(2))
                odds_2 = float(odds_match.group(3))
            else:
                # If pattern fails, try to find any three numbers
                numbers = re.findall(r'(\d+\.\d+)', odds_text)
                if len(numbers) >= 3:
                    odds_1 = float(numbers[0])
                    odds_x = float(numbers[1])
                    odds_2 = float(numbers[2])
                else:
                    print(f"  ⚠️ Could not parse odds: {odds_text[:50]}")
                    continue

            # 4. Convert kickoff string to datetime
            try:
                current_year = datetime.now().year
                kickoff = datetime.strptime(f"{current_year} {kickoff_str}", "%Y %d/%m %H:%M")

                # If date is in past, assume next year
                if kickoff < datetime.now():
                    kickoff = kickoff.replace(year=current_year + 1)

            except ValueError:
                kickoff = datetime.now() + timedelta(hours=1)

            # 5. Normalize names
            home_norm = normalize_name(home)
            away_norm = normalize_name(away)

            # 6. Create match entry
            match = {
                "match_id": f"{home_norm}-{away_norm}-football",
                "home": home,
                "away": away,
                "league": "Football",
                "kickoff": kickoff.strftime("%H:%M"),
                "kickoff_time": kickoff,
                "status": "Not Started",
                "odds_1": odds_1,
                "odds_x": odds_x,
                "odds_2": odds_2,
                "bookie": bookie_name,
                "normalized_full": f"{home_norm} vs {away_norm} in football"
            }
            matches.append(match)
            print(f"  ✅ {home} vs {away} @ {kickoff_str} - Odds: {odds_1}/{odds_x}/{odds_2}")

        except Exception as e:
            print(f"  ⚠️ Error parsing match: {e}")
            continue

    print(f"\nTotal matches extracted: {len(matches)}")
    return matches

