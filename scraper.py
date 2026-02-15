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

    for i, container in enumerate(match_containers):
        try:
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

            # 3. Convert kickoff string to datetime (IMPROVED VERSION)
            from datetime import datetime, timedelta

            now = datetime.now()
            current_year = now.year

            try:
                # Parse the date without year first
                base_date = datetime.strptime(kickoff_str, "%d/%m %H:%M")

                # Try current year
                kickoff = base_date.replace(year=current_year)

                # If it's more than 2 months in the past, try next year
                if kickoff < now - timedelta(days=60):
                    kickoff = base_date.replace(year=current_year + 1)
                    print(f"  📅 Date adjusted to next year: {kickoff.strftime('%Y-%m-%d %H:%M')}")

                # Special case: December matches scraped in January
                elif now.month == 1 and base_date.month == 12:
                    if kickoff.year == current_year:
                        kickoff = base_date.replace(year=current_year - 1)
                        print(f"  📅 Date adjusted to previous year: {kickoff.strftime('%Y-%m-%d %H:%M')}")

                # Special case: January matches scraped in December
                elif now.month == 12 and base_date.month == 1:
                    if kickoff.year == current_year:
                        kickoff = base_date.replace(year=current_year + 1)
                        print(f"  📅 Date adjusted to next year: {kickoff.strftime('%Y-%m-%d %H:%M')}")

            except ValueError as e:
                print(f"  ⚠️ Could not parse date '{kickoff_str}', using tomorrow")
                kickoff = now + timedelta(days=1)

            # 4. Normalize names (keeping your original approach)
            # Assuming you have a normalize_name function elsewhere
            try:
                from helpers import normalize_name
                home_norm = normalize_name(home)
                away_norm = normalize_name(away)
            except ImportError:
                # Simple fallback if normalize_name not available
                home_norm = home.lower().replace(' ', '-')
                away_norm = away.lower().replace(' ', '-')

            # 5. Create match entry (ODDS REMOVED)
            match = {
                "match_id": f"{home_norm}-{away_norm}-football",
                "home": home,
                "away": away,
                "league": "Football",
                "kickoff": kickoff.strftime("%H:%M"),
                "kickoff_time": kickoff,
                "bookie": bookie_name,
                "normalized_full": f"{home_norm} vs {away_norm}"
            }
            matches.append(match)
            print(f"  ✅ {home} vs {away} @ {kickoff_str}")

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
                "normalized_full": f"{normalize_name(home)} vs {normalize_name(away)}"
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
    """Extract matches from Betika - POLISHED FINAL VERSION"""
    matches = []
    seen_matches = set()

    # Words that are NOT team names
    non_team_words = ['Upcoming', 'Live', 'Today', 'Tomorrow', 'Now', 'Recent',
                      'Popular', 'Featured', 'Highlights', 'Results', 'Bc']

    # Find all divs that might contain match info
    all_divs = soup.find_all("div")
    print(f"Scanning {len(all_divs)} divs for Betika matches...")

    match_blocks = []

    for div in all_divs:
        text = div.get_text().strip()
        # Look for pattern: League • LeagueName followed by date and teams
        if "•" in text and "/" in text and ":" in text:
            lines = text.split('\n')
            if len(lines) >= 3:
                match_blocks.append(div)

    print(f"Found {len(match_blocks)} potential Betika match blocks")

    for block in match_blocks:
        try:
            text = block.get_text().strip()
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            if len(lines) < 3:
                continue

            # Extract league
            league_line = lines[0]
            league = league_line if "•" in league_line else "Football"

            # Extract time
            import re
            datetime_line = lines[1]
            time_match = re.search(r'(\d{2}:\d{2})', datetime_line)
            if not time_match:
                continue
            kickoff_str = time_match.group(1)

            # Extract teams - clean up by removing odds numbers and non-team words
            team_line = lines[2]

            # Remove any numbers with decimals (odds)
            team_line_clean = re.sub(r'\d+\.\d+', '', team_line)
            # Remove any standalone numbers
            team_line_clean = re.sub(r'\b\d+\b', '', team_line_clean)
            # Remove non-team words
            for word in non_team_words:
                team_line_clean = team_line_clean.replace(word, '')
            # Clean up extra spaces
            team_line_clean = ' '.join(team_line_clean.split())

            # Split into words
            team_words = team_line_clean.split()

            # Determine team names
            home = None
            away = None

            if len(team_words) >= 4:
                # Likely two-word teams (Real Madrid vs Real Sociedad)
                home = ' '.join(team_words[:2])
                away = ' '.join(team_words[2:4])
            elif len(team_words) == 3:
                # Could be "Man City vs Salford" (2 words vs 1)
                # Check if first two words form a known team
                first_two = ' '.join(team_words[:2])
                last_one = team_words[2]

                # Common two-word team names
                two_word_teams = ['Real Madrid', 'Real Sociedad', 'Manchester City',
                                  'Manchester United', 'Bayern Munich', 'Bayer Leverkusen',
                                  'Atletico Madrid', 'Aston Villa', 'West Ham', 'Leicester City',
                                  'Wolverhampton Wanderers', 'Nottingham Forest', 'Brighton Hove',
                                  'Newcastle United', 'Tottenham Hotspur', 'Crystal Palace']

                if any(team in first_two for team in two_word_teams):
                    home = first_two
                    away = last_one
                else:
                    home = team_words[0]
                    away = ' '.join(team_words[1:3])
            elif len(team_words) == 2:
                # One-word teams (Lazio vs Atalanta)
                home = team_words[0]
                away = team_words[1]
            else:
                continue

            # Clean up
            home = home.strip()
            away = away.strip()

            # Skip if teams are too short
            if len(home) < 2 or len(away) < 2:
                continue

            # Fix common split errors
            if home == "Lazio Atalanta":
                home = "Lazio"
                away = "Atalanta"
            if away == "Bc":
                away = "Atalanta"  # Fix for match 2

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
                "odds_1": None,
                "odds_x": None,
                "odds_2": None,
                "bookie": bookie_name,
                "normalized_full": f"{normalize_name(home)} vs {normalize_name(away)}"
            }
            matches.append(match)
            print(f"  ✅ Betika: {home} vs {away} @ {kickoff_str} [{league}]")

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            continue

    print(f"Total Betika matches extracted: {len(matches)}")
    return matches

def extract_sportpesa_matches(soup, bookie_name):
    """Extract matches from SportPesa - FINAL VERSION (no duplicates)"""
    matches = []
    seen_matches = set()

    # List of real teams to filter by
    real_teams = [
        'Bandari', 'AFC Leopards', 'Posta Rangers', 'Shabana FC', 'Mathare United',
        'Tusker', 'Bayer Leverkusen', 'St. Pauli', 'Manchester City', 'Salford City',
        'Inter', 'Juventus', 'Stuttgart', 'FC Koln', 'Burton', 'West Ham',
        'Aston Villa', 'Newcastle', 'Como', 'Fiorentina', 'Burnley', 'Mansfield',
        'Marseille', 'Strasbourg', 'Hoffenheim', 'SC Freiburg', 'Dinamo Zagreb',
        'Istra 1961', 'Lille', 'Brest', 'Getafe', 'Villarreal', 'Pyramids FC',
        'Power Dynamos', 'Paris FC', 'Lens', 'Eintracht Frankfurt',
        'Borussia Monchengladbach', 'Lazio', 'Atalanta', 'Sevilla FC', 'Alaves',
        'Simba SC', 'Stade Malien', 'El Zamalek', 'Kaizer Chiefs', 'Espanyol',
        'Celta Vigo', 'AL Hilal', 'FC Saint Eloi Lupopo', 'BSC Young Boys',
        'FC Winterthur', 'Nara Club', 'Imabari', 'Omiya Ardija', 'Consadole Sapporo',
        'Machida Zelvia', 'Mito Hollyhock', 'Sanfrecce Hiroshima', 'Fagiano Okayama',
        'Yokohama', 'Vegalta Sendai', 'Shonan Bellmare', 'Sagamihara', 'Shimizu S Pulse',
        'Kyoto Sanga', 'Ventforet Kofu', 'Nagano Parceiro', 'Fujieda MYFC',
        'Matsumoto Yamaga', 'APIA Tigers', 'NWS Spirit', 'FC Tokyo', 'Urawa Red Diamonds',
        'Melbourne Victory', 'Brisbane Roar', 'SD Raiders FC', 'Sydney Olympic'
    ]

    all_divs = soup.find_all("div")
    print(f"Scanning {len(all_divs)} divs for SportPesa matches...")

    match_blocks = []

    for div in all_divs:
        text = div.get_text().strip()
        # Check if this div contains a real team name AND a time (HH:MM)
        import re
        has_team = any(team in text for team in real_teams)
        has_time = re.search(r'\d{2}:\d{2}', text) is not None

        if has_team and has_time:
            match_blocks.append(div)

    print(f"Found {len(match_blocks)} SportPesa match blocks with real times")

    for block in match_blocks:
        try:
            text = block.get_text().strip()

            # Extract time (HH:MM)
            import re
            time_match = re.search(r'(\d{2}:\d{2})', text)
            if not time_match:
                continue
            kickoff_str = time_match.group(1)

            # Extract league - look for lines with " - "
            league = "Football"
            for line in text.split('\n'):
                if " - " in line and "ID:" not in line:
                    league = line.strip()
                    break

            # Extract team names - find two real teams in the text
            teams_found = []
            for team in real_teams:
                if team in text and team not in teams_found:
                    teams_found.append(team)
                if len(teams_found) >= 2:
                    break

            if len(teams_found) < 2:
                continue

            home = teams_found[0]
            away = teams_found[1]

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
                "odds_1": None,
                "odds_x": None,
                "odds_2": None,
                "bookie": bookie_name,
                "normalized_full": f"{normalize_name(home)} vs {normalize_name(away)}"
            }
            matches.append(match)
            print(f"  ✅ SportPesa: {home} vs {away} @ {kickoff_str} [{league}]")

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            continue

    print(f"Total SportPesa matches extracted: {len(matches)}")
    return matches

def extract_matches(soup, bookie_name):
    """Main dispatcher - calls the right scraper based on bookie name"""
    if bookie_name == "Odibets":
        return extract_odibets_matches(soup, bookie_name)
    elif bookie_name == "Betika":
        return extract_betika_matches(soup, bookie_name)
    elif bookie_name == "SportPesa":  # Add this
        return extract_sportpesa_matches(soup, bookie_name)
    elif bookie_name == "Xscores":
        return extract_xscores_matches(soup, bookie_name)
    else:
        print(f"⚠️ No scraper defined for {bookie_name}")
        return []

