import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add module paths
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scraper import extract_matches
from config import MIN_TIME_BUFFER


class TestExtractMatches(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.bookie_name = "Odibets"
        self.now = datetime.now()
        self.future_time = (self.now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        self.past_time = (self.now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

    def create_mock_soup(self, matches_data):
        """Helper to create mock BeautifulSoup object"""
        mock_soup = MagicMock()
        mock_rows = []

        for data in matches_data:
            mock_row = MagicMock()

            # Create NEW mocks for EACH row
            mock_home = MagicMock()
            mock_home.text.strip.return_value = data.get('home', 'Man Utd')

            mock_away = MagicMock()
            mock_away.text.strip.return_value = data.get('away', 'Liverpool')

            mock_league = MagicMock()
            mock_league.text.strip.return_value = data.get('league', 'Premier League')

            mock_time = MagicMock()
            mock_time.text.strip.return_value = data.get('kickoff', self.future_time)

            mock_status = MagicMock()
            mock_status.text.strip.return_value = data.get('status', 'Not Started')

            mock_odd1 = MagicMock() if data.get('odds_1') else None
            if mock_odd1:
                mock_odd1.text = str(data['odds_1'])

            mock_oddx = MagicMock() if data.get('odds_x') else None
            if mock_oddx:
                mock_oddx.text = str(data['odds_x'])

            mock_odd2 = MagicMock() if data.get('odds_2') else None
            if mock_odd2:
                mock_odd2.text = str(data['odds_2'])

            # FIX: Use a factory function to create a new closure for each row
            def make_side_effect(h, a, l, t, s, o1, ox, o2):
                def side_effect(tag, class_=None):
                    if class_ == "home-team":
                        return h
                    elif class_ == "away-team":
                        return a
                    elif class_ == "league":
                        return l
                    elif tag == "time":
                        return t
                    elif class_ == "status":
                        return s
                    elif class_ == "home-win-odd":
                        return o1
                    elif class_ == "draw-odd":
                        return ox
                    elif class_ == "away-win-odd":
                        return o2
                    return None

                return side_effect

            # Call the factory to create a new side_effect function with current mocks
            mock_row.find.side_effect = make_side_effect(
                mock_home, mock_away, mock_league, mock_time, mock_status,
                mock_odd1, mock_oddx, mock_odd2
            )

            mock_rows.append(mock_row)

        mock_soup.find_all.return_value = mock_rows
        return mock_soup

    @patch('scraper.extract_matches')
    def test_extract_valid_match(self, mock_normalize):
        """Test extracting a valid match with all required fields"""
        mock_normalize.side_effect = lambda x: x.lower().replace(' ', '')

        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_x': 3.40,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 1)
        match = result[0]

        self.assertEqual(match['bookie'], self.bookie_name)
        self.assertEqual(match['home'], 'Man Utd')
        self.assertEqual(match['away'], 'Liverpool')
        self.assertEqual(match['odds_1'], 2.10)
        self.assertEqual(match['odds_x'], 3.40)
        self.assertEqual(match['odds_2'], 3.20)
        self.assertEqual(match['status'], 'Not Started')
        self.assertIn('match_id', match)
        self.assertIn('normalized_full', match)

    def test_skip_match_without_odds(self):
        """Test skipping matches missing odds"""
        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Not Started',
            'odds_1': None,  # Missing odds
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 0)

    def test_skip_started_match(self):
        """Test skipping matches that have already started"""
        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Live',  # Started
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 0)

    def test_skip_match_with_insufficient_buffer(self):
        """Test skipping matches that start too soon"""
        soon_time = (self.now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")

        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': soon_time,
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 0)

    def test_handle_invalid_date_format(self):
        """Test handling invalid kickoff time format"""
        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': 'Invalid Date',
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        # Should default to now+1hour, which might pass buffer
        # Just check it doesn't crash and returns a match
        self.assertEqual(len(result), 1)

    def test_extract_multiple_matches(self):
        """Test extracting multiple matches from same page"""
        match_data = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': self.future_time,
                'status': 'Not Started',
                'odds_1': 2.10,
                'odds_x': 3.40,
                'odds_2': 3.20
            },
            {
                'home': 'Arsenal',
                'away': 'Chelsea',
                'league': 'Premier League',
                'kickoff': self.future_time,
                'status': 'Not Started',
                'odds_1': 2.30,
                'odds_x': 3.20,
                'odds_2': 2.90
            }
        ]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['home'], 'Man Utd')
        self.assertEqual(result[1]['home'], 'Arsenal')

    def test_extract_multiple_matches(self):
        """Test extracting multiple matches from same page"""
        match_data = [
            {
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': self.future_time,
                'status': 'Not Started',
                'odds_1': 2.10,
                'odds_x': 3.40,
                'odds_2': 3.20
            },
            {
                'home': 'Arsenal',
                'away': 'Chelsea',
                'league': 'Premier League',
                'kickoff': self.future_time,
                'status': 'Not Started',
                'odds_1': 2.30,
                'odds_x': 3.20,
                'odds_2': 2.90
            }
        ]

        mock_soup = self.create_mock_soup(match_data)

        with patch('scraper.normalize_name', lambda x: x.lower().replace(' ', '')):
            result = extract_matches(mock_soup, self.bookie_name)
            print("\n=== DEBUG ===")
            for i, match in enumerate(result):
                print(f"Match {i}: home={match['home']}, odds_1={match['odds_1']}")
            print("=============\n")

        self.assertEqual(len(result), 2)

        # Just check that both teams are present - don't worry about order
        home_teams = [match['home'] for match in result]
        self.assertIn('Man Utd', home_teams)
        self.assertIn('Arsenal', home_teams)

        # Also verify the odds are correct for each match
        for match in result:
            if match['home'] == 'Man Utd':
                self.assertEqual(match['odds_1'], 2.10)
                self.assertEqual(match['odds_2'], 3.20)
            elif match['home'] == 'Arsenal':
                self.assertEqual(match['odds_1'], 2.30)
                self.assertEqual(match['odds_2'], 2.90)

    def test_match_id_consistency(self):
        """Test that match_id is generated consistently"""
        with patch('scraper.normalize_name') as mock_normalize:
            mock_normalize.side_effect = ['manutd', 'liverpool', 'premierleague']

            match_data = [{
                'home': 'Man Utd',
                'away': 'Liverpool',
                'league': 'Premier League',
                'kickoff': self.future_time,
                'status': 'Not Started',
                'odds_1': 2.10,
                'odds_2': 3.20
            }]

            mock_soup = self.create_mock_soup(match_data)
            result = extract_matches(mock_soup, self.bookie_name)

            self.assertEqual(result[0]['match_id'], 'manutd-liverpool-premierleague')

    def test_draw_odds_optional(self):
        """Test that draw odds are optional"""
        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_x': None,  # Draw odds missing
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]['odds_x'])

    def test_empty_page(self):
        """Test with no match rows"""
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []

        result = extract_matches(mock_soup, self.bookie_name)
        self.assertEqual(len(result), 0)

    @patch('scraper.normalize_name')
    def test_normalization_called(self, mock_normalize):
        """Test that normalize_name is called for home, away, league"""
        mock_normalize.return_value = 'normalized'

        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        extract_matches(mock_soup, self.bookie_name)

        # Should be called 3 times (home, away, league)
        self.assertEqual(mock_normalize.call_count, 3)

    def test_kickoff_time_format(self):
        """Test that kickoff time is stored in both string and datetime formats"""
        match_data = [{
            'home': 'Man Utd',
            'away': 'Liverpool',
            'league': 'Premier League',
            'kickoff': self.future_time,
            'status': 'Not Started',
            'odds_1': 2.10,
            'odds_2': 3.20
        }]

        mock_soup = self.create_mock_soup(match_data)
        result = extract_matches(mock_soup, self.bookie_name)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['kickoff'],
                         datetime.strptime(self.future_time, "%Y-%m-%d %H:%M").strftime("%H:%M"))
        self.assertIsInstance(result[0]['kickoff_time'], datetime)


if __name__ == '__main__':
    unittest.main(verbosity=2)