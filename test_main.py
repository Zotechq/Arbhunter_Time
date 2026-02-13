import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import main_loop, request_counter


class TestMainLoop(unittest.TestCase):

    def setUp(self):
        """Reset global request_counter before each test"""
        global request_counter
        request_counter = 0

        # Sample test data
        self.mock_matches = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': '20:00',
                'kickoff_time': datetime.now(),
                'status': 'Not Started',
                'odds_1': 2.10,
                'odds_2': 3.20,
                'bookie': 'Odibets',
                'match_id': 'manutd-liverpool-pl',
                'normalized_full': 'manutd vs liverpool in premierleague'
            },
            {
                'home': 'Arsenal',
                'away': 'Chelsea',
                'league': 'Premier League',
                'kickoff': '17:30',
                'kickoff_time': datetime.now(),
                'status': 'Not Started',
                'odds_1': 2.30,
                'odds_2': 2.90,
                'bookie': 'Flashscore',
                'match_id': 'arsenal-chelsea-pl',
                'normalized_full': 'arsenal vs chelsea in premierleague'
            }
        ]

        self.mock_variations = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'majority_time': '20:00',
                'outlier_bookies': ['Odibets'],
                'variation_gap_minutes': 15
            }
        ]

        self.mock_arbs = [
            {
                'match': 'Man Utd vs Liverpool',
                'bookie_1': 'Odibets',
                'odds_1': 2.10,
                'bookie_2': 'Betway',
                'odds_2': 3.20,
                'arb_percentage': 2.5
            }
        ]

    def tearDown(self):
        """Clean up after each test"""
        global request_counter
        request_counter = 0

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_main_loop_successful_run(self, mock_detect_arbs, mock_display_variations,
                                      mock_detect_variations, mock_log_csv, mock_display_matches,
                                      mock_extract, mock_fetch):
        """Test successful main loop execution with matches"""
        import main
        # Force reset the counter directly in the module
        main.request_counter = 0

        # Setup mocks
        mock_fetch.return_value = MagicMock()
        mock_extract.return_value = self.mock_matches
        mock_detect_variations.return_value = self.mock_variations
        mock_detect_arbs.return_value = self.mock_arbs

        # Run
        main.main_loop()  # Use main.main_loop() instead of just main_loop()

        # Assert fetch_page was called with counter = 1
        mock_fetch.assert_called_once_with('https://example.com/odds', 1)

        # ... rest of assertions
    @patch('main.BOOKMAKER_URLS', [
        ('https://example.com/odds1', 'Bookie1'),
        ('https://example.com/odds2', 'Bookie2')
    ])
    @patch('main.BOOKMAKER_URLS', [  # This does NOT add a mock parameter
        ('https://example.com/odds1', 'Bookie1'),
        ('https://example.com/odds2', 'Bookie2')
    ])
    @patch('main.fetch_page')  # +1 mock
    @patch('main.extract_matches')  # +1 mock
    @patch('main.display_matches')  # +1 mock
    @patch('main.log_to_csv')  # +1 mock
    @patch('main.detect_variations')  # +1 mock
    @patch('main.display_time_variations')  # +1 mock
    @patch('main.detect_arbs')  # +1 mock
    def test_main_loop_multiple_bookmakers(self,
                                           mock_detect_arbs,  # 1
                                           mock_display_variations,  # 2
                                           mock_detect_variations,  # 3
                                           mock_log_csv,  # 4
                                           mock_display_matches,  # 5
                                           mock_extract,  # 6
                                           mock_fetch):  # 7
        """Test main loop with multiple bookmakers"""
        # ... test body

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_main_loop_no_matches(self,
                                  mock_detect_arbs,  # 1
                                  mock_display_variations,  # 2
                                  mock_detect_variations,  # 3
                                  mock_log_csv,  # 4
                                  mock_display_matches,  # 5
                                  mock_extract,  # 6
                                  mock_fetch):  # 7
        """Test main loop when no matches are found"""
        # Reset counter at start of test
        global request_counter
        request_counter = 0

        # Setup mocks
        mock_fetch.return_value = MagicMock()
        mock_extract.return_value = []  # No matches

        # Run
        with patch('builtins.print') as mock_print:
            main_loop()

        # Assert display_matches was not called
        mock_display_matches.assert_not_called()

        # Assert log_to_csv was not called
        mock_log_csv.assert_not_called()

        # Assert detect_variations was not called
        mock_detect_variations.assert_not_called()

        # Assert display_time_variations was not called
        mock_display_variations.assert_not_called()

        # Assert detect_arbs was not called
        mock_detect_arbs.assert_not_called()

        # Assert "No matches this cycle" was printed
        mock_print.assert_any_call("No matches this cycle.")

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_main_loop_fetch_fails(self, mock_detect_arbs, mock_display_variations,
                                   mock_detect_variations, mock_log_csv, mock_display_matches,
                                   mock_extract, mock_fetch):
        """Test main loop when fetch_page returns None"""
        # Reset counter at start of test
        global request_counter
        request_counter = 0

        # Setup mocks
        mock_fetch.return_value = None  # Fetch failed

        # Run
        main_loop()

        # Assert extract_matches was not called
        mock_extract.assert_not_called()

        # Assert display_matches was not called
        mock_display_matches.assert_not_called()

        # Assert log_to_csv was not called
        mock_log_csv.assert_not_called()

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_main_loop_no_variations(self, mock_detect_arbs, mock_display_variations,
                                     mock_detect_variations, mock_log_csv, mock_display_matches,
                                     mock_extract, mock_fetch):
        """Test main loop when no time variations are detected"""
        # Reset counter at start of test
        global request_counter
        request_counter = 0

        # Setup mocks
        mock_fetch.return_value = MagicMock()
        mock_extract.return_value = self.mock_matches
        mock_detect_variations.return_value = []  # No variations
        mock_detect_arbs.return_value = []  # No arbs

        # Run
        main_loop()

        # Assert display_time_variations was not called
        mock_display_variations.assert_not_called()

        # Assert log_to_csv was called for matches only
        mock_log_csv.assert_called_once_with(self.mock_matches, 'oddbets_matches.csv')

        # Assert detect_arbs was called
        mock_detect_arbs.assert_called_once()

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_main_loop_no_arbs(self, mock_detect_arbs, mock_display_variations,
                               mock_detect_variations, mock_log_csv, mock_display_matches,
                               mock_extract, mock_fetch):
        """Test main loop when no arbitrage opportunities are found"""
        # Reset counter at start of test
        global request_counter
        request_counter = 0

        # Setup mocks
        mock_fetch.return_value = MagicMock()
        mock_extract.return_value = self.mock_matches
        mock_detect_variations.return_value = self.mock_variations  # Has variations
        mock_detect_arbs.return_value = []  # No arbs

        # Run
        main_loop()

        # Assert log_to_csv was called for matches and variations
        expected_calls = [
            call(self.mock_matches, 'oddbets_matches.csv'),
            call(self.mock_variations, 'oddbets_matches_with_varying_times.csv')
        ]
        mock_log_csv.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(mock_log_csv.call_count, 2)

    @patch('main.BOOKMAKER_URLS', [('https://example.com/odds', 'TestBookie')])
    @patch('main.fetch_page')
    @patch('main.extract_matches')
    @patch('main.display_matches')
    @patch('main.log_to_csv')
    @patch('main.detect_variations')
    @patch('main.display_time_variations')
    @patch('main.detect_arbs')
    def test_request_counter_increment(self, mock_detect_arbs, mock_display_variations,
                                       mock_detect_variations, mock_log_csv, mock_display_matches,
                                       mock_extract, mock_fetch):
        """Test that request_counter increments correctly"""
        # Use patch to directly set the global variable
        import main
        with patch('main.request_counter', 5):  # Patch the global variable
            mock_fetch.return_value = MagicMock()
            mock_extract.return_value = self.mock_matches
            mock_detect_variations.return_value = []
            mock_detect_arbs.return_value = []

            # Run
            main_loop()

            # Assert counter was incremented
            mock_fetch.assert_called_once_with('https://example.com/odds', 6)
            self.assertEqual(main.request_counter, 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)