import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
import csv
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from output import display_matches, display_time_variations, log_to_csv


class TestDisplayMatches(unittest.TestCase):

    def setUp(self):
        self.empty_matches = []
        self.single_match = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': '20:00',
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        self.multiple_matches = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': '20:00',
                'status': 'Not Started',
            },
            {
                'home': 'Arsenal',
                'away': 'Chelsea',
                'league': 'Premier League',
                'kickoff': '17:30',
                'status': 'Not Started',
            }
        ]

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_matches_empty(self, mock_stdout):
        """Test displaying empty matches list"""
        display_matches(self.empty_matches)
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, "No matches to display.")

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_matches_single(self, mock_stdout):
        """Test displaying single match"""
        display_matches(self.single_match)
        output = mock_stdout.getvalue()

        self.assertIn("Man Utd", output)
        self.assertIn("Liverpool", output)
        self.assertIn("Premier League", output)
        self.assertIn("20:00", output)
        self.assertIn("Not Started", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_matches_multiple(self, mock_stdout):
        """Test displaying multiple matches"""
        display_matches(self.multiple_matches)
        output = mock_stdout.getvalue()

        self.assertIn("Man Utd", output)
        self.assertIn("Liverpool", output)
        self.assertIn("Arsenal", output)
        self.assertIn("Chelsea", output)
        self.assertIn("20:00", output)
        self.assertIn("17:30", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_matches_headers(self, mock_stdout):
        """Test table headers are displayed"""
        display_matches(self.single_match)
        output = mock_stdout.getvalue()

        self.assertIn("Home", output)
        self.assertIn("Away", output)
        self.assertIn("League", output)
        self.assertIn("Time", output)
        self.assertIn("Status", output)


class TestDisplayTimeVariations(unittest.TestCase):

    def setUp(self):
        self.empty_variations = []

        self.single_variation = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'majority_time': '20:00',
            'outlier_bookies': ['Odibets'],
            'variation_gap_minutes': 15
        }]

        self.multiple_variations = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'majority_time': '20:00',
                'outlier_bookies': ['Odibets'],
                'variation_gap_minutes': 15
            },
            {
                'home': 'Arsenal',
                'away': 'Chelsea',
                'league': 'Premier League',
                'majority_time': '17:30',
                'outlier_bookies': ['Betway', 'SportyBet'],
                'variation_gap_minutes': 30
            }
        ]

        self.multiple_outliers = [{
            'home': 'Man City',
            'away': 'Tottenham',
            'league': 'Premier League',
            'majority_time': '19:45',
            'outlier_bookies': ['Odibets', 'Bet365', 'Betway'],
            'variation_gap_minutes': 45
        }]

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_variations_empty(self, mock_stdout):
        """Test displaying empty variations list"""
        display_time_variations(self.empty_variations)
        output = mock_stdout.getvalue()

        # Should print table with no data rows
        self.assertIn("Match", output)
        self.assertIn("League", output)
        self.assertIn("Majority Time", output)
        self.assertIn("Outlier Bookie(s)", output)
        self.assertIn("Gap (mins)", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_variations_single(self, mock_stdout):
        """Test displaying single time variation"""
        display_time_variations(self.single_variation)
        output = mock_stdout.getvalue()

        self.assertIn("Man Utd vs Liverpool", output)
        self.assertIn("Premier League", output)
        self.assertIn("20:00", output)
        self.assertIn("Odibets", output)
        self.assertIn("15", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_variations_multiple(self, mock_stdout):
        """Test displaying multiple time variations"""
        display_time_variations(self.multiple_variations)
        output = mock_stdout.getvalue()

        self.assertIn("Man Utd vs Liverpool", output)
        self.assertIn("Arsenal vs Chelsea", output)
        self.assertIn("Betway, SportyBet", output)
        self.assertIn("30", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_variations_multiple_outliers(self, mock_stdout):
        """Test displaying variation with multiple outlier bookies"""
        display_time_variations(self.multiple_outliers)
        output = mock_stdout.getvalue()

        self.assertIn("Man City vs Tottenham", output)
        self.assertIn("Odibets, Bet365, Betway", output)
        self.assertIn("45", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_variations_formatting(self, mock_stdout):
        """Test table headers are correct"""
        display_time_variations(self.single_variation)
        output = mock_stdout.getvalue()

        self.assertIn("Match", output)
        self.assertIn("League", output)
        self.assertIn("Majority Time", output)
        self.assertIn("Outlier Bookie(s)", output)
        self.assertIn("Gap (mins)", output)


class TestLogToCSV(unittest.TestCase):

    def setUp(self):
        self.empty_data = []

        self.single_match = [{
            'match_id': 'manutd-liverpool-premierleague',
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': '20:00',
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20,
            'bookie': 'Odibets'
        }]

        self.multiple_matches = [
            {
                'match_id': 'manutd-liverpool-premierleague',
                'home': 'Man Utd',
                'away': 'Liverpool',
                'odds_1': 2.10,
                'odds_2': 3.20,
                'bookie': 'Odibets'
            },
            {
                'match_id': 'arsenal-chelsea-premierleague',
                'home': 'Arsenal',
                'away': 'Chelsea',
                'odds_1': 2.30,
                'odds_2': 2.90,
                'bookie': 'Betway'
            }
        ]

        self.variation_data = [{
            'match': 'Man Utd vs Liverpool',
            'league': 'Premier League',
            'majority_time': '20:00',
            'outliers': 'Odibets',
            'gap_minutes': 15
        }]

    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    def test_log_to_csv_empty(self, mock_dictwriter, mock_file):
        """Test logging empty data to CSV"""
        log_to_csv(self.empty_data, 'test.csv')
        mock_file.assert_not_called()
        mock_dictwriter.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_single_match(self, mock_file):
        """Test logging single match to CSV"""
        filename = 'matches.csv'
        log_to_csv(self.single_match, filename)

        mock_file.assert_called_once_with(filename, 'a', newline='', encoding='utf-8')

        # Verify writer was created and methods called
        handle = mock_file()
        writer = csv.DictWriter
        writer.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_multiple_matches(self, mock_file):
        """Test logging multiple matches to CSV"""
        filename = 'matches.csv'
        log_to_csv(self.multiple_matches, filename)

        mock_file.assert_called_once_with(filename, 'a', newline='', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_writes_header_when_file_empty(self, mock_file):
        """Test header is written when file is new/empty"""
        mock_file.return_value.tell.return_value = 0

        log_to_csv(self.single_match, 'test.csv')

        # Get the writer instance and check writeheader was called
        handle = mock_file()
        writer = csv.DictWriter(handle, fieldnames=self.single_match[0].keys())

        # We need to patch DictWriter to actually check this
        with patch('csv.DictWriter') as mock_dictwriter:
            log_to_csv(self.single_match, 'test.csv')
            mock_dictwriter.return_value.writeheader.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_skips_header_when_file_not_empty(self, mock_file):
        """Test header is not written when file already has data"""
        mock_file.return_value.tell.return_value = 100  # File not empty

        with patch('csv.DictWriter') as mock_dictwriter:
            log_to_csv(self.single_match, 'test.csv')
            mock_dictwriter.return_value.writeheader.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_writerows_called(self, mock_file):
        """Test writerows is called with correct data"""
        with patch('csv.DictWriter') as mock_dictwriter:
            mock_writer = MagicMock()
            mock_dictwriter.return_value = mock_writer

            log_to_csv(self.single_match, 'test.csv')

            mock_writer.writerows.assert_called_once_with(self.single_match)

    @patch('builtins.open', new_callable=mock_open)
    def test_log_to_csv_multiple_calls_same_file(self, mock_file):
        """Test appending to same file multiple times"""
        with patch('csv.DictWriter') as mock_dictwriter:
            mock_writer = MagicMock()
            mock_dictwriter.return_value = mock_writer

            # First call - new file
            mock_file.return_value.tell.return_value = 0
            log_to_csv(self.single_match, 'test.csv')

            # Second call - existing file
            mock_file.return_value.tell.return_value = 100
            log_to_csv(self.multiple_matches, 'test.csv')

            self.assertEqual(mock_dictwriter.call_count, 2)
            self.assertEqual(mock_writer.writerows.call_count, 2)

    def test_log_to_csv_actual_file_write(self):
        """Integration test: actually write to a temporary CSV file"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            filename = temp_file.name

        try:
            # Write data
            log_to_csv(self.single_match, filename)

            # Read it back
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['home'], 'Man Utd')
                self.assertEqual(rows[0]['away'], 'Liverpool')
                self.assertEqual(rows[0]['bookie'], 'Odibets')

            # Append more data
            log_to_csv(self.multiple_matches, filename)

            # Read again - should have 3 rows now
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 3)

        finally:
            os.unlink(filename)


class TestIntegration(unittest.TestCase):
    """Test the output functions working together"""

    def test_full_output_pipeline(self):
        """Test matches → display → CSV pipeline"""
        matches = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': '20:00',
                'status': 'Not Started',
                'odds_1': 2.10,
                'odds_2': 3.20,
                'bookie': 'Odibets',
                'match_id': 'manutd-liverpool-pl'
            }
        ]

        variations = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'majority_time': '20:00',
                'outlier_bookies': ['Betway'],
                'variation_gap_minutes': 15
            }
        ]

        # Test display functions don't crash
        with patch('sys.stdout', new_callable=StringIO):
            display_matches(matches)
            display_time_variations(variations)

        # Test CSV logging
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            filename = temp_file.name

        try:
            log_to_csv(matches, filename)
            with open(filename, 'r') as f:
                content = f.read()
                self.assertIn('Man Utd', content)
                self.assertIn('Liverpool', content)
        finally:
            os.unlink(filename)


if __name__ == '__main__':
    unittest.main(verbosity=2)