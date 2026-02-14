# engine.py
# New focus: Time-Discrepancy Hunting as primary detection
# detect_variations is now the main function
# detect_arbs is kept but deprioritized (no console output)

from collections import defaultdict, Counter
from datetime import timedelta
from config import TIME_VARIATION_THRESHOLD_MINUTES, MIN_ARB_PCT
from helpers import fuzzy_match, group_fuzzy_matches  # Assuming you have this from fuzzy


def detect_variations(matches, threshold_minutes=2):
    """Detect matches with different kickoff times across bookmakers"""
    from helpers import fuzzy_match
    from collections import defaultdict, Counter

    # Group matches
    match_groups = defaultdict(list)

    for match in matches:
        norm_full = match['normalized_full']

        # Find matching group
        found = False
        for key in list(match_groups.keys()):
            if fuzzy_match(norm_full, key):
                match_groups[key].append(match)
                found = True
                break

        if not found:
            match_groups[norm_full].append(match)

    # Find variations
    variations = []

    for group_key, group_matches in match_groups.items():
        if len(group_matches) < 2:
            continue

        # Get times for each bookmaker
        bookie_times = {}
        for match in group_matches:
            bookie = match['bookie']
            if match.get('kickoff_time'):
                bookie_times[bookie] = match['kickoff_time'].strftime('%H:%M')

        if len(bookie_times) < 2:
            continue

        # Find majority time
        times_list = list(bookie_times.values())
        time_counts = Counter(times_list)
        majority_time = time_counts.most_common(1)[0][0]

        # Find outliers
        outliers = []
        for bookie, time in bookie_times.items():
            if time != majority_time:
                gap = 0
                # Find a match with this time to calculate gap
                for match in group_matches:
                    if match['bookie'] == bookie and match.get('kickoff_time'):
                        for m2 in group_matches:
                            if m2['kickoff_time'] and m2['bookie'] != bookie:
                                gap = abs((match['kickoff_time'] - m2['kickoff_time']).total_seconds() / 60)
                                break
                        break

                if gap >= threshold_minutes:
                    outliers.append({
                        'bookie': bookie,
                        'time': time,
                        'gap': gap
                    })

        if outliers:
            # Get all times for display
            odibets_time = bookie_times.get('Odibets', '—')
            betika_time = bookie_times.get('Betika', '—')
            xscores_time = bookie_times.get('Xscores', '—')

            # Use first match for details
            first_match = group_matches[0]

            variations.append({
                'match': f"{first_match['home']} vs {first_match['away']}",
                'league': first_match['league'],
                'majority_time': majority_time,
                'outlier_bookies': [o['bookie'] for o in outliers],
                'variation_gap_minutes': outliers[0]['gap'],
                'odibets_time': odibets_time,
                'betika_time': betika_time,
                'xscores_time': xscores_time
            })

    return variations


def is_profitable_opportunity(match_times, current_time):
    """
    Determine if a time variation is actually profitable

    Returns: (is_profitable, reason, strategy)
    """
    # match_times = {
    #   'Odibets': '19:00',
    #   'Betika': '20:00',
    #   'Xscores': '20:00',
    #   'real_time': '20:00'  # We need this!
    # }

    # Find which bookmaker is EARLIER (behind)
    times = []
    for bookie, time_str in match_times.items():
        if bookie != 'real_time' and time_str != '—':
            try:
                hour, minute = map(int, time_str.split(':'))
                time_obj = current_time.replace(hour=hour, minute=minute, second=0)
                times.append((bookie, time_obj))
            except:
                continue

    if len(times) < 2:
        return False, "Not enough data", None

    # Sort by time (earliest first)
    times.sort(key=lambda x: x[1])
    earliest_bookie, earliest_time = times[0]
    latest_bookie, latest_time = times[-1]

    # Calculate minutes difference
    gap_minutes = (latest_time - earliest_time).total_seconds() / 60

    # Check if earliest time is in the PAST
    if earliest_time < current_time:
        return False, f"Match already started ({earliest_time.strftime('%H:%M')})", None

    # Check if latest time is BEFORE earliest (shouldn't happen but just in case)
    if latest_time < earliest_time:
        return False, "Time logic error", None

    # PROFITABLE! The earliest bookie is behind, but match hasn't started
    if gap_minutes >= 30:  # Minimum 30 min window to be useful
        strategy = f"Bet on {latest_bookie} (shows {latest_time.strftime('%H:%M')}) " \
                   f"after checking {earliest_bookie}'s app at {earliest_time.strftime('%H:%M')}"
        return True, f"{earliest_bookie} is {gap_minutes:.0f}min behind", strategy

    return False, f"Only {gap_minutes:.0f}min window - too small", None


def detect_profitable_variations(matches):
    """
    Detect ONLY variations that are actually profitable
    (where the behind bookmaker's game hasn't started yet)
    """
    from helpers import fuzzy_match
    from collections import defaultdict
    from datetime import datetime

    current_time = datetime.now()
    profitable_opportunities = []

    # Group matches
    match_groups = defaultdict(list)

    for match in matches:
        if not match.get('kickoff_time'):
            continue
        norm_full = match['normalized_full']

        # Find matching group
        found = False
        for key in list(match_groups.keys()):
            if fuzzy_match(norm_full, key):
                match_groups[key].append(match)
                found = True
                break

        if not found:
            match_groups[norm_full].append(match)

    # Analyze each group
    for group_key, group_matches in match_groups.items():
        if len(group_matches) < 2:
            continue

        # Collect times by bookmaker
        bookie_times = {}
        for match in group_matches:
            bookie = match['bookie']
            if match.get('kickoff_time'):
                bookie_times[bookie] = match['kickoff_time']

        if len(bookie_times) < 2:
            continue

        # Find the earliest and latest times
        times_list = list(bookie_times.values())
        earliest_time = min(times_list)
        latest_time = max(times_list)

        # Find which bookies have which times
        earliest_bookies = [b for b, t in bookie_times.items() if t == earliest_time]
        latest_bookies = [b for b, t in bookie_times.items() if t == latest_time]

        gap_minutes = (latest_time - earliest_time).total_seconds() / 60

        # CRITICAL CHECK: Is the earliest time in the FUTURE?
        if earliest_time > current_time:
            # GAME HASN'T STARTED - this is PROFITABLE!
            if gap_minutes >= 15:  # At least 15 min window
                first_match = group_matches[0]

                # Determine strategy
                if len(earliest_bookies) == 1 and len(latest_bookies) >= 1:
                    # One bookie is behind, others are correct
                    behind_bookie = earliest_bookies[0]
                    correct_bookies = latest_bookies

                    strategy = f"🎯 PROFIT: {behind_bookie} is {gap_minutes:.0f}min behind. " \
                               f"Match starts at {earliest_time.strftime('%H:%M')} (per {behind_bookie}) " \
                               f"but actually at {latest_time.strftime('%H:%M')} (per {', '.join(correct_bookies)}). " \
                               f"You can bet on {behind_bookie} website until {earliest_time.strftime('%H:%M')}!"

                    profitable_opportunities.append({
                        'match': f"{first_match['home']} vs {first_match['away']}",
                        'league': first_match.get('league', 'Football'),
                        'behind_bookie': behind_bookie,
                        'behind_time': earliest_time.strftime('%H:%M'),
                        'correct_time': latest_time.strftime('%H:%M'),
                        'correct_bookies': correct_bookies,
                        'gap_minutes': round(gap_minutes, 1),
                        'window_until': earliest_time.strftime('%H:%M'),
                        'strategy': strategy,
                        'confidence': 'HIGH' if gap_minutes > 30 else 'MEDIUM'
                    })

        else:
            # Game already started - NOT profitable
            print(f"⏰ Skipping {group_key} - already started at {earliest_time.strftime('%H:%M')}")

    return profitable_opportunities


def analyze_all_discrepancies(all_matches):
    """Analyze all matches across bookmakers to find who's wrong"""
    from helpers import fuzzy_match
    from collections import defaultdict
    from datetime import datetime

    # Group matches by normalized name
    match_groups = defaultdict(list)

    for match in all_matches:
        if not match.get('kickoff_time'):
            continue

        norm_full = match['normalized_full']

        # Find matching group
        found = False
        for key in list(match_groups.keys()):
            if fuzzy_match(norm_full, key):
                match_groups[key].append(match)
                found = True
                break

        if not found:
            match_groups[norm_full].append(match)

    # Analyze each group
    discrepancies = []

    for group_key, group_matches in match_groups.items():
        if len(group_matches) < 2:
            continue

        # Collect all times by bookmaker
        bookie_times = {}
        for match in group_matches:
            bookie = match['bookie']
            kickoff = match['kickoff_time']
            bookie_times[bookie] = kickoff

        if len(bookie_times) < 2:
            continue

        # Find the most common time (majority)
        from collections import Counter
        times_list = [t.strftime('%H:%M') for t in bookie_times.values()]
        time_counts = Counter(times_list)
        majority_time_str = time_counts.most_common(1)[0][0]

        # Convert majority time string to datetime.time for comparison
        majority_time_obj = datetime.strptime(majority_time_str, '%H:%M').time()

        # Find which bookies are wrong
        wrong_bookies = []
        all_times_display = {}  # 👈 CREATE THIS DICTIONARY

        for bookie, kickoff_dt in bookie_times.items():
            time_str = kickoff_dt.strftime('%H:%M')
            all_times_display[bookie] = time_str  # 👈 STORE ALL TIMES HERE

            if time_str != majority_time_str:
                # Calculate gap in minutes
                from datetime import datetime, timedelta
                today = datetime.now().date()
                kickoff_datetime = datetime.combine(today, kickoff_dt.time())
                majority_datetime = datetime.combine(today, majority_time_obj)
                gap = abs((kickoff_datetime - majority_datetime).total_seconds() / 60)

                wrong_bookies.append({
                    'bookie': bookie,
                    'their_time': time_str,
                    'gap_minutes': gap
                })

        if wrong_bookies:
            # Get match details from first match
            first_match = group_matches[0]

            discrepancies.append({
                'match': f"{first_match['home']} vs {first_match['away']}",
                'league': first_match.get('league', 'Football'),
                'correct_time': majority_time_str,
                'wrong_bookies': wrong_bookies,
                'all_times': all_times_display,  # 👈 ADD THIS KEY
                'gap_summary': "\n".join([f"{w['bookie']}: {w['gap_minutes']:.0f}min" for w in wrong_bookies])
            })

    return discrepancies

def detect_arbs(matches, min_profit_pct=1.2):
    """Detect arbitrage opportunities across bookmakers (deprioritized)"""
    from helpers import fuzzy_match

    # Group matches by normalized names (use string keys)
    match_groups = {}

    for match in matches:
        norm_full = match['normalized_full']

        # Find matching group
        found_group = None
        for group_name in match_groups.keys():
            if fuzzy_match(norm_full, group_name):
                found_group = group_name
                break

        if found_group:
            match_groups[found_group].append(match)
        else:
            match_groups[norm_full] = [match]

    # Find arbs within each group
    arbs = []

    for group_name, group_matches in match_groups.items():
        if len(group_matches) < 2:
            continue

        # Look for best odds across bookmakers
        best_odds = {
            '1': {'value': 0, 'bookie': None, 'match': None},
            'X': {'value': 0, 'bookie': None, 'match': None},
            '2': {'value': 0, 'bookie': None, 'match': None}
        }

        for match in group_matches:
            # Track best home odds
            if match.get('odds_1') and match['odds_1'] > best_odds['1']['value']:
                best_odds['1'] = {'value': match['odds_1'], 'bookie': match['bookie'], 'match': match}

            # Track best draw odds
            if match.get('odds_x') and match['odds_x'] > best_odds['X']['value']:
                best_odds['X'] = {'value': match['odds_x'], 'bookie': match['bookie'], 'match': match}

            # Track best away odds
            if match.get('odds_2') and match['odds_2'] > best_odds['2']['value']:
                best_odds['2'] = {'value': match['odds_2'], 'bookie': match['bookie'], 'match': match}

        # Check if we have all three odds
        if best_odds['1']['value'] > 0 and best_odds['X']['value'] > 0 and best_odds['2']['value'] > 0:
            # Calculate arb percentage
            arb_pct = (1 / best_odds['1']['value'] + 1 / best_odds['X']['value'] + 1 / best_odds['2']['value']) * 100

            if arb_pct < 100:
                profit_pct = 100 - arb_pct
                if profit_pct >= min_profit_pct:
                    arbs.append({
                        'match': f"{best_odds['1']['match']['home']} vs {best_odds['1']['match']['away']}",
                        'bookie_1': best_odds['1']['bookie'],
                        'odds_1': best_odds['1']['value'],
                        'bookie_X': best_odds['X']['bookie'],
                        'odds_X': best_odds['X']['value'],
                        'bookie_2': best_odds['2']['bookie'],
                        'odds_2': best_odds['2']['value'],
                        'arb_percentage': round(profit_pct, 2)
                    })

    return arbs