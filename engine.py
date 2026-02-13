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

    # Group matches by normalized names (use string keys, not dicts)
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

    # Find variations within each group
    variations = []

    for group_name, group_matches in match_groups.items():
        if len(group_matches) < 2:
            continue

        # Get all kickoff times
        times = [m['kickoff_time'] for m in group_matches if m.get('kickoff_time')]
        if not times:
            continue

        # Find the most common time (majority)
        from collections import Counter
        time_counts = Counter(times)
        majority_time = time_counts.most_common(1)[0][0]

        # Find outliers
        for match in group_matches:
            if match.get('kickoff_time') and match['kickoff_time'] != majority_time:
                gap = abs((match['kickoff_time'] - majority_time).total_seconds() / 60)

                if gap >= threshold_minutes:
                    variations.append({
                        'home': match['home'],
                        'away': match['away'],
                        'league': match.get('league', 'Football'),
                        'majority_time': majority_time.strftime('%H:%M'),
                        'outlier_bookies': [match['bookie']],
                        'variation_gap_minutes': round(gap, 1)
                    })

    return variations


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