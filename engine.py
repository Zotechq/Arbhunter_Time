# engine.py
# New focus: Time-Discrepancy Hunting as primary detection
# detect_variations is now the main function
# detect_arbs is kept but deprioritized (no console output)

from collections import defaultdict, Counter
from datetime import timedelta
from config import TIME_VARIATION_THRESHOLD_MINUTES, MIN_ARB_PCT
from helpers import fuzzy_match, group_fuzzy_matches  # Assuming you have this from fuzzy


def detect_variations(matches):
    grouped = defaultdict(list)
    group_keys = []

    for m in matches:
        norm_full = m['normalized_full']
        group_key = group_fuzzy_matches(norm_full, group_keys, 0.8)
        if group_key not in group_keys:
            group_keys.append(group_key)
        grouped[group_key].append(m)

    variations = []

    for group_key, group in grouped.items():
        if len(group) < 2:
            continue

        times_by_bookie = {m['bookie']: m['kickoff_time'] for m in group}
        all_times = list(times_by_bookie.values())

        if len(set(all_times)) == 1:
            continue

        majority_time = Counter(all_times).most_common(1)[0][0]
        min_time = min(all_times)
        max_time = max(all_times)
        gap = (max_time - min_time).total_seconds() / 60.0

        if gap < TIME_VARIATION_THRESHOLD_MINUTES:
            continue

        outliers = [bookie for bookie, t in times_by_bookie.items() if
                    abs((t - majority_time).total_seconds() / 60.0) > TIME_VARIATION_THRESHOLD_MINUTES]

        # Get odds from outliers for logging (if available)
        outlier_odds = {bookie: {'odds_1': next((m['odds_1'] for m in group if m['bookie'] == bookie), None),
                                 'odds_x': next((m['odds_x'] for m in group if m['bookie'] == bookie), None),
                                 'odds_2': next((m['odds_2'] for m in group if m['bookie'] == bookie), None)} for bookie
                        in outliers}

        variations.append({
            "match_id": group_key,
            "home": group[0]['home'],
            "away": group[0]['away'],
            "league": group[0]['league'],
            "reported_times": {b: t.strftime("%H:%M") for b, t in times_by_bookie.items()},
            "outlier_bookies": outliers,
            "variation_gap_minutes": round(gap, 1),
            "majority_time": majority_time.strftime("%H:%M"),
            "outlier_odds": outlier_odds  # For logging stale odds
        })

    return variations


def detect_arbs(matches, min_arb_pct=MIN_ARB_PCT):
    # Kept for optional logging – no console output
    arbs = []
    grouped = defaultdict(list)
    group_keys = []

    for m in matches:
        norm_full = m['normalized_full']
        group_key = group_fuzzy_matches(norm_full, group_keys, 0.8)
        if group_key not in group_keys:
            group_keys.append(group_key)
        grouped[group_key].append(m)

    for group_key, group in grouped.items():
        best_1 = max(odd['odds_1'] for odd in group if odd['odds_1'])
        best_x = max(odd['odds_x'] for odd in group if odd['odds_x']) if any(odd['odds_x'] for odd in group) else None
        best_2 = max(odd['odds_2'] for odd in group if odd['odds_2'])

        imp_1 = 1 / best_1
        imp_x = 1 / best_x if best_x else 0
        imp_2 = 1 / best_2

        total_imp = imp_1 + imp_x + imp_2

        if total_imp < 1 and total_imp > 0:
            arb_pct = (1 / total_imp - 1) * 100
            if arb_pct >= min_arb_pct:
                match = group[0]
                arb = {
                    "match_id": group_key,
                    "home": match['home'],
                    "away": match['away'],
                    "league": match['league'],
                    "kickoff": match['kickoff'],
                    "arb_pct": round(arb_pct, 2),
                    "best_odds": {"1": best_1, "X": best_x, "2": best_2},
                    "bookies": {
                        "1": next(odd['bookie'] for odd in group if odd['odds_1'] == best_1),
                        "X": next(odd['bookie'] for odd in group if odd['odds_x'] == best_x) if best_x else None,
                        "2": next(odd['bookie'] for odd in group if odd['odds_2'] == best_2)
                    }
                }
                arbs.append(arb)
    return arbs