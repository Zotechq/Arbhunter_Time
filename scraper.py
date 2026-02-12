from datetime import datetime, timedelta
from helpers import normalize_name
from config import MIN_TIME_BUFFER
from network import fetch_page


def extract_matches(soup, bookie_name):
    matches = []
    # Hypothetical parsing – customize based on site's HTML (use Inspect tool)
    for row in soup.find_all("div", class_="match-row"):  # Adjust classes
        home = row.find("span", class_="home-team").text.strip()
        away = row.find("span", class_="away-team").text.strip()
        league = row.find("div", class_="league").text.strip()
        kickoff_str = row.find("time").text.strip()  # e.g., "2026-02-09 20:00"
        status = row.find("span", class_="status").text.strip()
        odds_1 = float(row.find("span", class_="home-win-odd").text) if row.find("span",
                                                                                 class_="home-win-odd") else None
        odds_x = float(row.find("span", class_="draw-odd").text) if row.find("span", class_="draw-odd") else None
        odds_2 = float(row.find("span", class_="away-win-odd").text) if row.find("span",
                                                                                 class_="away-win-odd") else None


        try:
            kickoff = datetime.strptime(kickoff_str, "%Y-%m-%d %H:%M")
        except ValueError:
            kickoff = datetime.now() + timedelta(hours=1)

            # Normalize for initial match_id
            home_norm = normalize_name(home)
            away_norm = normalize_name(away)
            league_norm = normalize_name(league)
            match_id = f"{home_norm}-{away_norm}-{league_norm}"

            if status.lower() == "not started" and kickoff > datetime.now() + MIN_TIME_BUFFER and odds_1 and odds_2:
                matches.append({
                    "match_id": match_id,  # Initial – fuzzy will refine grouping
                    "home": home,  # Original names kept for display
                    "away": away,
                    "league": league,
                    "kickoff": kickoff.strftime("%H:%M"),
                    "kickoff_time": kickoff,  # Full datetime for variations
                    "status": status,
                    "odds_1": odds_1,
                    "odds_x": odds_x,
                    "odds_2": odds_2,
                    "bookie": bookie_name,
                    "normalized_full": f"{home_norm} vs {away_norm} in {league_norm}"  # For fuzzy matching
                })

    return matches