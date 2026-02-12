import unittest
import re
from helpers import (
    abbrev_map,
    stop_words,
    normalize_name,
    levenshtein_distance,
    fuzzy_match,
    group_fuzzy_matches
)


class TestNormalizeName(unittest.TestCase):

    def test_lowercase_conversion(self):
        self.assertEqual(normalize_name("Man Utd"), "manchester united")

    def test_abbreviation_expansion(self):
        self.assertEqual(normalize_name("man utd"), "manchester united")
        self.assertEqual(normalize_name("ars"), "arsenal")
        self.assertEqual(normalize_name("lfc"), "liverpool")
        self.assertEqual(normalize_name("rm"), "real madrid")
        self.assertEqual(normalize_name("fcb"), "bayern munich")
        self.assertEqual(normalize_name("mci"), "manchester city")
        self.assertEqual(normalize_name("tot"), "tottenham")
        self.assertEqual(normalize_name("bar"), "barcelona")
        self.assertEqual(normalize_name("atm"), "atletico madrid")
        self.assertEqual(normalize_name("psg"), "paris saint germain")
        self.assertEqual(normalize_name("juv"), "juventus")
        self.assertEqual(normalize_name("int"), "inter milan")
        self.assertEqual(normalize_name("mil"), "ac milan")
        self.assertEqual(normalize_name("nap"), "napoli")

    def test_stop_word_removal(self):
        self.assertEqual(normalize_name("manchester united fc"), "manchester united")
        self.assertEqual(normalize_name("real madrid club"), "real madrid")
        self.assertEqual(normalize_name("ac milan"), "ac milan")  # 'ac' not in stop_words
        self.assertEqual(normalize_name("st etienne"), "etienne")
        self.assertEqual(normalize_name("bayern munich sc"), "bayern munich")
        self.assertEqual(normalize_name("chelsea bc"), "chelsea")

    def test_special_characters_removal(self):
        self.assertEqual(normalize_name("man-utd!"), "manchester united")
        self.assertEqual(normalize_name("arsenal fc."), "arsenal")
        self.assertEqual(normalize_name("barcelona@cf"), "barcelona")
        self.assertEqual(normalize_name("liverpool#$%"), "liverpool")
        self.assertEqual(normalize_name("real_madrid"), "real madrid")

    def test_multiple_abbreviations(self):
        self.assertEqual(normalize_name("man utd fc"), "manchester united")
        self.assertEqual(normalize_name("man city"), "manchester city")
        self.assertEqual(normalize_name("rm cf"), "real madrid")

    def test_empty_string(self):
        self.assertEqual(normalize_name(""), "")

    def test_only_stop_words(self):
        self.assertEqual(normalize_name("fc sc"), "")
        self.assertEqual(normalize_name("club st bc"), "")

    def test_no_changes_needed(self):
        self.assertEqual(normalize_name("chelsea"), "chelsea")
        self.assertEqual(normalize_name("liverpool"), "liverpool")
        self.assertEqual(normalize_name("arsenal"), "arsenal")


class TestLevenshteinDistance(unittest.TestCase):

    def test_identical_strings(self):
        self.assertEqual(levenshtein_distance("united", "united"), 0)
        self.assertEqual(levenshtein_distance("", ""), 0)
        self.assertEqual(levenshtein_distance("manchester", "manchester"), 0)

    def test_completely_different(self):
        self.assertEqual(levenshtein_distance("arsenal", "chelsea"), 7)
        self.assertEqual(levenshtein_distance("liverpool", "manchester"), 9)

    def test_one_character_difference(self):
        self.assertEqual(levenshtein_distance("united", "unite"), 1)
        self.assertEqual(levenshtein_distance("man", "manu"), 1)
        self.assertEqual(levenshtein_distance("madrid", "madird"), 2)

    def test_empty_string(self):
        self.assertEqual(levenshtein_distance("", "united"), 6)
        self.assertEqual(levenshtein_distance("manchester", ""), 10)

    def test_case_sensitivity(self):
        self.assertGreater(levenshtein_distance("United", "united"), 0)
        self.assertEqual(levenshtein_distance("United", "United"), 0)

    def test_different_lengths(self):
        self.assertEqual(levenshtein_distance("man", "manchester"), 6)
        self.assertEqual(levenshtein_distance("lfc", "liverpool"), 6)


class TestFuzzyMatch(unittest.TestCase):

    def test_exact_match_after_normalization(self):
        self.assertTrue(fuzzy_match("man utd", "manchester united"))
        self.assertTrue(fuzzy_match("ars", "arsenal"))
        self.assertTrue(fuzzy_match("lfc", "liverpool fc"))
        self.assertTrue(fuzzy_match("rm", "real madrid"))
        self.assertTrue(fuzzy_match("mci", "manchester city"))

    def test_close_match_above_threshold(self):
        self.assertTrue(fuzzy_match("man united", "manchester united"))
        self.assertTrue(fuzzy_match("real madird", "real madrid"))  # typo
        self.assertTrue(fuzzy_match("barca", "barcelona"))
        self.assertTrue(fuzzy_match("man utd", "manchester untd"))  # typo
        self.assertTrue(fuzzy_match("bayern", "bayern munich"))

    def test_different_match_below_threshold(self):
        self.assertFalse(fuzzy_match("arsenal", "chelsea"))
        self.assertFalse(fuzzy_match("liverpool", "manchester"))
        self.assertFalse(fuzzy_match("real", "barcelona"))
        self.assertFalse(fuzzy_match("juventus", "inter milan"))

    def test_custom_threshold(self):
        # Lower threshold should match more
        self.assertTrue(fuzzy_match("ars", "arsenal", threshold=0.3))
        self.assertTrue(fuzzy_match("man", "manchester", threshold=0.4))
        # Higher threshold should match less
        self.assertFalse(fuzzy_match("ars", "arsenal", threshold=0.9))
        self.assertFalse(fuzzy_match("man", "manchester", threshold=0.9))

    def test_edge_cases(self):
        self.assertTrue(fuzzy_match("", ""))
        self.assertFalse(fuzzy_match("", "united"))
        self.assertTrue(fuzzy_match("man utd", "man utd"))
        self.assertTrue(fuzzy_match("", "", threshold=0.5))

    def test_stop_word_impact(self):
        self.assertTrue(fuzzy_match("manchester united fc", "man utd"))
        self.assertTrue(fuzzy_match("ac milan", "milan"))  # 'ac' preserved
        self.assertTrue(fuzzy_match("real madrid cf", "rm"))

    def test_abbreviation_handling(self):
        self.assertTrue(fuzzy_match("mci", "manchester city"))
        self.assertTrue(fuzzy_match("psg", "paris saint germain"))
        self.assertTrue(fuzzy_match("juv", "juventus"))
        self.assertTrue(fuzzy_match("int", "inter milan"))
        self.assertTrue(fuzzy_match("mil", "ac milan"))
        self.assertTrue(fuzzy_match("nap", "napoli"))

    def test_similar_but_different_teams(self):
        self.assertFalse(fuzzy_match("man utd", "man city"))
        self.assertFalse(fuzzy_match("ac milan", "inter milan"))
        self.assertFalse(fuzzy_match("real madrid", "atletico madrid"))


class TestGroupFuzzyMatches(unittest.TestCase):

    def test_basic_grouping(self):
        names = ["man utd", "manchester united", "man united", "arsenal", "ars"]
        groups = group_fuzzy_matches(names)

        self.assertEqual(len(groups), 2)

        # Find the groups
        for group_name, group_list in groups.items():
            if "man" in group_name.lower():
                self.assertIn("man utd", group_list)
                self.assertIn("manchester united", group_list)
                self.assertIn("man united", group_list)
                self.assertEqual(len(group_list), 3)
            elif "ars" in group_name.lower():
                self.assertIn("arsenal", group_list)
                self.assertIn("ars", group_list)
                self.assertEqual(len(group_list), 2)

    def test_no_matches(self):
        names = ["arsenal", "chelsea", "liverpool", "man city"]
        groups = group_fuzzy_matches(names)

        self.assertEqual(len(groups), 4)
        for group in groups.values():
            self.assertEqual(len(group), 1)

    def test_all_match(self):
        names = ["man utd", "man united", "manchester utd", "manchester united"]
        groups = group_fuzzy_matches(names)

        self.assertEqual(len(groups), 1)
        group_list = list(groups.values())[0]
        self.assertEqual(len(group_list), 4)
        for name in names:
            self.assertIn(name, group_list)

    def test_custom_threshold(self):
        names = ["ars", "arsenal", "arsenalfc", "tot", "tottenham"]

        # Strict threshold
        strict_groups = group_fuzzy_matches(names, threshold=0.9)
        self.assertGreaterEqual(len(strict_groups), 3)

        # Loose threshold
        loose_groups = group_fuzzy_matches(names, threshold=0.5)
        self.assertLessEqual(len(loose_groups), 2)

    def test_duplicate_names(self):
        names = ["man utd", "man utd", "man united"]
        groups = group_fuzzy_matches(names)

        self.assertEqual(len(groups), 1)
        self.assertEqual(len(list(groups.values())[0]), 3)

    def test_empty_list(self):
        groups = group_fuzzy_matches([])
        self.assertEqual(groups, {})

    def test_order_independence(self):
        names1 = ["man utd", "arsenal", "man united"]
        names2 = ["man united", "arsenal", "man utd"]

        groups1 = group_fuzzy_matches(names1)
        groups2 = group_fuzzy_matches(names2)

        self.assertEqual(len(groups1), len(groups2))

    def test_threshold_boundaries(self):
        names = ["man utd", "manchester city"]

        # Should not match at default threshold
        groups_default = group_fuzzy_matches(names)
        self.assertEqual(len(groups_default), 2)

        # Should match at very low threshold
        groups_low = group_fuzzy_matches(names, threshold=0.3)
        self.assertEqual(len(groups_low), 1)


class TestIntegration(unittest.TestCase):
    """Test the complete pipeline together"""

    def test_real_world_scenario(self):
        team_variations = [
            "man utd", "manchester utd", "man united", "mufc",
            "arsenal", "ars", "afc",
            "lfc", "liverpool", "liverpool fc",
            "cfc", "chelsea fc", "chelsea",
            "rm", "real madrid", "real",
            "fcb", "bayern", "bayern munich"
        ]

        groups = group_fuzzy_matches(team_variations)

        # Should have 6 groups (Man Utd, Arsenal, Liverpool, Chelsea, Real Madrid, Bayern)
        self.assertEqual(len(groups), 6)

        # Check each group has reasonable size
        for group in groups.values():
            self.assertGreaterEqual(len(group), 2)
            self.assertLessEqual(len(group), 4)

    def test_fuzzy_match_vs_grouping_consistency(self):
        """Individual fuzzy_match should agree with grouping"""
        name1 = "man utd"
        name2 = "manchester united"
        name3 = "chelsea"

        self.assertTrue(fuzzy_match(name1, name2))
        self.assertFalse(fuzzy_match(name1, name3))

        groups = group_fuzzy_matches([name1, name2, name3])

        # Find which group contains name1
        group_for_name1 = None
        for group in groups.values():
            if name1 in group:
                group_for_name1 = group
                break

        self.assertIsNotNone(group_for_name1)
        self.assertIn(name2, group_for_name1)
        self.assertNotIn(name3, group_for_name1)

    def test_normalize_then_fuzzy_consistency(self):
        """Normalization should produce same fuzzy results"""
        raw_name = "Man Utd FC!"
        normalized = normalize_name(raw_name)

        self.assertEqual(normalized, "manchester united")
        self.assertTrue(fuzzy_match(raw_name, "manchester united"))
        self.assertTrue(fuzzy_match(raw_name, "man utd"))


if __name__ == '__main__':
    unittest.main(verbosity=2)