import unittest
from helpers import fuzzy_match, normalize_name
from engine import detect_arbs

class TestFuzzyMatch(unittest.TestCase):
    def test_variations(self):
        self.assertTrue(fuzzy_match("Man Utd", "Manchester United"))
        self.assertTrue(fuzzy_match("Manchester United", "United Manchester FC"))
        self.assertFalse(fuzzy_match("Man Utd", "Liverpool FC"))

class TestDetectArbs(unittest.TestCase):
    def test_basic_arb_detection(self):
        test_matches = [
            {'match_id': 'test', 'home': 'TeamA', 'away': 'TeamB', 'league': 'TestLeague', 'kickoff': '20:00',
             'odds_1': 2.5, 'odds_x': 4.0, 'odds_2': 5.0, 'bookie': 'Bookie1', 'normalized_full': 'teama vs teamb in testleague'},
            {'match_id': 'test', 'home': 'Team A', 'away': 'Team B FC', 'league': 'Test League', 'kickoff': '20:00',
             'odds_1': 2.1, 'odds_x': 3.4, 'odds_2': 4.0, 'bookie': 'Bookie2', 'normalized_full': 'teama vs teamb in testleague'}
        ]
        arbs = detect_arbs(test_matches, min_arb_pct=1.0)
        self.assertEqual(len(arbs), 1)
        self.assertGreater(arbs[0]['arb_pct'], 1.0)