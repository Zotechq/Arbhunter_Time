import unittest


class TestTeamMatching(unittest.TestCase):

    # 1. Testing the "Cleaning Station"
    def test_normalize_name(self):
        # Scenario: Bookmaker uses capital letters and abbreviations
        # "Man Utd" should become "united" because 'man' is removed and 'utd' expanded
        from helpers import normalize_name
        self.assertEqual(normalize_name("Man Utd"), "manchester")

        # Scenario: Bookmaker adds punctuation or 'boring' words like FC
        # "Arsenal F.C." should just become "arsenal"
        self.assertEqual(normalize_name("Arsenal F.C."), "arsenal")

    def test_fuzzy_match_success(self):
            # Scenario: Two bookmakers spell a team slightly differently
            # These should be recognized as the SAME team (Signal)
            name1 = "Manchester United"
            name2 = "Man Utd"
            from helpers import fuzzy_match
            self.assertTrue(fuzzy_match(name1, name2, threshold=0.7))

    def test_fuzzy_match_failure(self):
            # Scenario: Two different teams that share a word
            # "Manchester United" and "Manchester City" should NOT match (Noise)
            from helpers import fuzzy_match
            self.assertFalse(fuzzy_match("Manchester United", "Manchester City", threshold=0.9))
