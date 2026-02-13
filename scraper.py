import re
from datetime import datetime, timedelta
from helpers import normalize_name
from config import MIN_TIME_BUFFER
from network import fetch_page


def extract_odibets_matches(soup, bookie_name):
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


def extract_xscores_matches(soup, bookie_name):
    """Extract matches from Xscores"""
    matches = []

    # Find all match containers - multiple possible classes
    match_containers = soup.find_all("div", class_=lambda c: c and ('match_line_upper' in c or 'match_line_lower' in c))
    print(f"Found {len(match_containers)} Xscores match containers")

    for container in match_containers:
        try:
            # 1. Get kickoff time
            time_elem = container.find("div", class_="score_ko")
            if not time_elem:
                time_elem = container.find("div", id="ko_time")
            kickoff_str = time_elem.text.strip() if time_elem else "20:00"

            # 2. Get match status (live, HT, FT, SCH)
            status_elem = container.find("div", class_="score-status")
            status = status_elem.text.strip() if status_elem else "SCH"

            # Skip finished matches (only want upcoming/scheduled)
            if status in ["FT", "FTR", "FIN", "AET"]:
                continue

            # 3. Get league/tournament
            league_elem = container.find("div", class_="score_league_txt")
            league = league_elem.text.strip() if league_elem else "Football"

            # 4. Get team names - try multiple possible classes
            home_elem = container.find("div", class_="score_home_txt")
            away_elem = container.find("div", class_="score_away_txt")

            # If not found, try searching by text pattern
            if not home_elem or not away_elem:
                # Look for any divs with team names (they often appear multiple times)
                all_text = container.get_text().split()
                # Find potential team names (words with capital letters)
                import re
                potential_teams = [word for word in all_text if re.match(r'^[A-Z][a-z]+', word) and len(word) > 2]
                if len(potential_teams) >= 2:
                    home = potential_teams[0]
                    away = potential_teams[1]
                else:
                    continue
            else:
                home = home_elem.text.strip()
                away = away_elem.text.strip()

            # Skip if no valid team names
            if not home or not away or home.isdigit() or away.isdigit():
                continue

            # 5. Xscores doesn't show odds directly - we'll need to mark as N/A
            # or we can try to find odds in a different part of the page

            # Convert kickoff string to datetime
            try:
                from datetime import datetime, timedelta
                now = datetime.now()
                # Handle format like "12:00" or "14:00"
                if ":" in kickoff_str:
                    hour, minute = map(int, kickoff_str.split(':'))
                    kickoff = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    # If time already passed today, assume tomorrow
                    if kickoff < now:
                        kickoff += timedelta(days=1)
                else:
                    kickoff = now + timedelta(hours=2)
            except:
                kickoff = datetime.now() + timedelta(hours=2)

            # 6. Create match entry (same format as Odibets)
            match = {
                "match_id": f"{normalize_name(home)}-{normalize_name(away)}-football",
                "home": home,
                "away": away,
                "league": league,
                "kickoff": kickoff.strftime("%H:%M"),
                "kickoff_time": kickoff,
                "status": "Not Started" if status == "SCH" else status,
                "odds_1": None,  # Xscores doesn't have odds
                "odds_x": None,
                "odds_2": None,
                "bookie": bookie_name,
                "normalized_full": f"{normalize_name(home)} vs {normalize_name(away)} in {normalize_name(league)}"
            }
            matches.append(match)
            print(f"  ✅ Xscores: {home} vs {away} @ {kickoff_str} [{league}]")

        except Exception as e:
            print(f"  ⚠️ Error parsing Xscores match: {e}")
            continue

    if len(matches) > 0:
        print(f"  ✅ Extracted {len(matches)} Xscores matches (first: {matches[0]['home']} vs {matches[0]['away']})")
    return matches


def extract_betika_matches(soup, bookie_name):
    """Extract matches from Betika - IMPROVED VERSION"""
    matches = []
    seen_matches = set()

    # Method 1: Look for divs with match patterns
    all_divs = soup.find_all("div")
    print(f"Scanning {len(all_divs)} divs for Betika matches...")

    match_blocks = []

    # Common team names to look for
    team_keywords = ['Elche', 'Osasuna', 'Pisa', 'Milan', 'Dortmund', 'Mainz',
                     'Rennes', 'Psg', 'Monaco', 'Nantes', 'Wrexham', 'Ipswich',
                     'Hull', 'Chelsea', 'Volendam', 'Psv', 'Galatasaray',
                     'Eyupspor', 'Santa Clara', 'Benfica', 'Antalyaspor', 'Samsunspor']

    for div in all_divs:
        text = div.get_text().strip()
        # Look for patterns that indicate a match
        if any(team in text for team in team_keywords):
            if "•" in text or ":" in text or any(odds in text for odds in [".", "odds"]):
                match_blocks.append(div)

    # Method 2: If no blocks found, try specific Betika structure
    if len(match_blocks) < 5:  # Not enough matches found
        # Try finding by common Betika classes
        for class_name in ['match', 'event', 'fixture', 'game-row']:
            elements = soup.find_all(class_=lambda c: c and class_name in str(c).lower() if c else False)
            match_blocks.extend(elements)

    print(f"Found {len(match_blocks)} potential Betika match blocks")

    for block in match_blocks:
        try:
            text = block.get_text().strip()

            # Extract odds - look for pattern like "2.90 3.20 2.70"
            import re
            odds_pattern = r'(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)'
            odds_match = re.search(odds_pattern, text)

            odds_1 = odds_x = odds_2 = None
            if odds_match:
                odds_1 = float(odds_match.group(1))
                odds_x = float(odds_match.group(2))
                odds_2 = float(odds_match.group(3))

            # Extract team names
            home = None
            away = None

            # Look for known team names
            for i, team in enumerate(team_keywords):
                if team in text:
                    # Find the second team
                    for team2 in team_keywords[i + 1:]:
                        if team2 in text:
                            home = team
                            away = team2
                            break
                    if home and away:
                        break

            # If teams not found by keywords, try to extract from text
            if not home or not away:
                # Remove odds from text to get team part
                if odds_match:
                    text_before_odds = text[:odds_match.start()].strip()
                    words = text_before_odds.split()
                    if len(words) >= 4:
                        home = ' '.join(words[:2])
                        away = ' '.join(words[-2:])
                    elif len(words) >= 2:
                        home = words[0]
                        away = words[1]
                    else:
                        continue
                else:
                    continue

            # Extract league
            league = "Football"
            league_keywords = ['LaLiga', 'Serie A', 'Bundesliga', 'Ligue 1', 'FA Cup',
                               'Eredivisie', 'Super Lig', 'Liga Portugal', 'Premier League']
            for l in league_keywords:
                if l in text:
                    league = l
                    break

            # Extract time
            time_match = re.search(r'(\d{2}:\d{2})', text)
            kickoff_str = time_match.group(1) if time_match else "20:00"

            # Create unique ID
            match_id = f"{home}-{away}-{league}"

            if match_id in seen_matches:
                continue

            seen_matches.add(match_id)

            # Parse kickoff
            from datetime import datetime, timedelta
            now = datetime.now()
            try:
                hour, minute = map(int, kickoff_str.split(':'))
                kickoff = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if kickoff < now:
                    kickoff += timedelta(days=1)
            except:
                kickoff = now + timedelta(hours=2)
                kickoff_str = kickoff.strftime("%H:%M")

            match = {
                "match_id": match_id,
                "home": home,
                "away": away,
                "league": league,
                "kickoff": kickoff_str,
                "kickoff_time": kickoff,
                "status": "Not Started",
                "odds_1": odds_1,
                "odds_x": odds_x,
                "odds_2": odds_2,
                "bookie": bookie_name,
                "normalized_full": f"{normalize_name(home)} vs {normalize_name(away)} in {normalize_name(league)}"
            }
            matches.append(match)
            print(f"  ✅ Betika: {home} vs {away} @ {kickoff_str} - {odds_1}/{odds_x}/{odds_2}")

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            continue

    print(f"Total unique Betika matches: {len(matches)}")
    return matches

def extract_matches(soup, bookie_name):
    """Main dispatcher - calls the right scraper based on bookie name"""
    if bookie_name == "Odibets":
        return extract_odibets_matches(soup, bookie_name)
    elif bookie_name == "Betika":
        return extract_betika_matches(soup, bookie_name)
    elif bookie_name == "Xscores":
        return extract_xscores_matches(soup, bookie_name)
    else:
        print(f"⚠️ No scraper defined for {bookie_name}")
        return []

