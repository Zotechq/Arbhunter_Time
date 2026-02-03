from collections import defaultdict

from datetime import datetime, timedelta

from config import MIN_ARB_PCT
from helpers import fuzzy_match

def find_fuzzy_group_key(normalized_full, existing_keys, threshold=0.8):
    """Find if normalized_full fuzzy matches any existing group key"""
    for key in existing_keys:
        if fuzzy_match(normalized_full, key, threshold):
            return key
    return normalized_full  # New group if no match


def detect_arbs(matches_from_all_bookies, min_arb_pct=MIN_ARB_PCT):
    arbs = []
    grouped_odds = defaultdict(list)
    group_keys = []  # Track existing normalized keys for fuzzy check

    for m in matches_from_all_bookies:
        norm_full = m['normalized_full']
        group_key = find_fuzzy_group_key(norm_full, group_keys, 0.8)
        if group_key not in group_keys:
            group_keys.append(group_key)
        grouped_odds[group_key].append(m)

    for group_key, match_group in grouped_odds.items():
        best_1 = max(odd['odds_1'] for odd in match_group if odd['odds_1'])
        best_x = max(odd['odds_x'] for odd in match_group if odd['odds_x']) if any(
            odd['odds_x'] for odd in match_group) else None
        best_2 = max(odd['odds_2'] for odd in match_group if odd['odds_2'])

        imp_1 = 1 / best_1
        imp_x = 1 / best_x if best_x else 0
        imp_2 = 1 / best_2

        total_imp = imp_1 + imp_x + imp_2

        if total_imp < 1 and total_imp > 0:
            arb_pct = (1 / total_imp - 1) * 100
            if arb_pct >= min_arb_pct:
                match = match_group[0]
                arb = {
                    "match_id": group_key,  # Fuzzy-resolved key
                    "home": match['home'],
                    "away": match['away'],
                    "league": match['league'],
                    "kickoff": match['kickoff'],
                    "arb_pct": round(arb_pct, 2),
                    "best_odds": {"1": best_1, "X": best_x, "2": best_2},
                    "bookies": {
                        "1": next(odd['bookie'] for odd in match_group if odd['odds_1'] == best_1),
                        "X": next(odd['bookie'] for odd in match_group if odd['odds_x'] == best_x) if best_x else None,
                        "2": next(odd['bookie'] for odd in match_group if odd['odds_2'] == best_2)
                    }
                }
                arbs.append(arb)
    return arbs


def detect_variations(matches):
    time_groups = defaultdict(list)
    group_keys = []

    for m in matches:
        norm_full = m['normalized_full']
        group_key = find_fuzzy_group_key(norm_full, group_keys, 0.8)
        if group_key not in group_keys:
            group_keys.append(group_key)
        time_groups[group_key].append(m['kickoff_time'])

    variations = []
    for group_key, times in time_groups.items():
        if max(times) - min(times) > timedelta(minutes=5):
            variations.append({"match_id": group_key, "time_variation": max(times) - min(times)})
    return variations