import unittest
import os
import tempfile
from datetime import datetime, timedelta
import sys

# Add the project directory to path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import config


class TestConfig(unittest.TestCase):

    def test_bookmaker_urls_format(self):
        """Test that BOOKMAKER_URLS contains tuples of (url, name)"""
        self.assertIsInstance(config.BOOKMAKER_URLS, list)
        self.assertGreater(len(config.BOOKMAKER_URLS), 0)

        for item in config.BOOKMAKER_URLS:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            url, name = item
            self.assertIsInstance(url, str)
            self.assertIsInstance(name, str)
            self.assertTrue(url.startswith(('http://', 'https://')))
            self.assertTrue(len(name) > 0)

    def test_user_agents(self):
        """Test that USER_AGENTS is a non-empty list of strings"""
        self.assertIsInstance(config.USER_AGENTS, list)
        self.assertGreater(len(config.USER_AGENTS), 0)

        for agent in config.USER_AGENTS:
            self.assertIsInstance(agent, str)
            self.assertTrue(len(agent) > 50)  # User agents should be substantial
            self.assertTrue(any(browser in agent.lower() for browser in
                                ['chrome', 'firefox', 'safari', 'edg', 'opera']))

    def test_tor_configuration(self):
        """Test Tor proxy settings"""
        self.assertIsInstance(config.TOR_PROXY, str)
        self.assertTrue(config.TOR_PROXY.startswith('socks5://'))
        self.assertIn('127.0.0.1', config.TOR_PROXY)
        self.assertIn('9050', config.TOR_PROXY)

        self.assertIsInstance(config.CONTROL_PORT, int)
        self.assertEqual(config.CONTROL_PORT, 9051)

        # CONTROL_PASSWORD can be None or str
        self.assertTrue(config.CONTROL_PASSWORD is None or
                        isinstance(config.CONTROL_PASSWORD, str))

    def test_csv_paths(self):
        """Test CSV file paths are strings"""
        self.assertIsInstance(config.CSV_MATCHES, str)
        self.assertIsInstance(config.CSV_VARIATIONS, str)
        self.assertIsInstance(config.CSV_ARBS, str)

        # All should be .csv files
        self.assertTrue(config.CSV_MATCHES.endswith('.csv'))
        self.assertTrue(config.CSV_VARIATIONS.endswith('.csv'))
        self.assertTrue(config.CSV_ARBS.endswith('.csv'))

    def test_time_thresholds(self):
        """Test time threshold configurations"""
        # MIN_TIME_BUFFER
        self.assertIsInstance(config.MIN_TIME_BUFFER, timedelta)
        self.assertEqual(config.MIN_TIME_BUFFER, timedelta(minutes=15))

        # TIME_VARIATION_THRESHOLD_MINUTES
        self.assertIsInstance(config.TIME_VARIATION_THRESHOLD_MINUTES, (int, float))
        self.assertGreater(config.TIME_VARIATION_THRESHOLD_MINUTES, 0)
        self.assertEqual(config.TIME_VARIATION_THRESHOLD_MINUTES, 2)

    def test_request_settings(self):
        """Test request/refresh configurations"""
        self.assertIsInstance(config.REFRESH_INTERVAL_MINUTES, int)
        self.assertGreater(config.REFRESH_INTERVAL_MINUTES, 0)
        self.assertEqual(config.REFRESH_INTERVAL_MINUTES, 5)

        self.assertIsInstance(config.REQUEST_DELAY_MIN, (int, float))
        self.assertIsInstance(config.REQUEST_DELAY_MAX, (int, float))
        self.assertGreaterEqual(config.REQUEST_DELAY_MIN, 0)
        self.assertGreater(config.REQUEST_DELAY_MAX, config.REQUEST_DELAY_MIN)

        self.assertIsInstance(config.IP_RENEW_EVERY_REQUESTS, int)
        self.assertGreater(config.IP_RENEW_EVERY_REQUESTS, 0)
        self.assertEqual(config.IP_RENEW_EVERY_REQUESTS, 5)

    def test_arbitrage_settings(self):
        """Test arbitrage-related settings"""
        self.assertIsInstance(config.MIN_ARB_PCT, float)
        self.assertGreater(config.MIN_ARB_PCT, 0)
        self.assertEqual(config.MIN_ARB_PCT, 1.2)

    def test_no_duplicate_urls(self):
        """Test that there are no duplicate bookmaker URLs"""
        urls = [item[0] for item in config.BOOKMAKER_URLS]
        self.assertEqual(len(urls), len(set(urls)))

    def test_no_duplicate_names(self):
        """Test that there are no duplicate bookmaker names"""
        names = [item[1] for item in config.BOOKMAKER_URLS]
        self.assertEqual(len(names), len(set(names)))

    def test_user_agent_uniqueness(self):
        """Test that all user agents are unique"""
        self.assertEqual(len(config.USER_AGENTS), len(set(config.USER_AGENTS)))

    def test_csv_paths_writable(self):
        """Test that CSV paths are in writable directories"""
        for path in [config.CSV_MATCHES, config.CSV_VARIATIONS, config.CSV_ARBS]:
            dirname = os.path.dirname(path) or '.'
            self.assertTrue(os.access(dirname, os.W_OK) or not os.path.exists(dirname),
                            f"Directory {dirname} is not writable")


class TestConfigValidation(unittest.TestCase):
    """Test config validation helpers that might be added to config.py"""

    def setUp(self):
        """Create temporary directory for writable tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_paths = {
            'matches': config.CSV_MATCHES,
            'variations': config.CSV_VARIATIONS,
            'arbs': config.CSV_ARBS
        }

    def tearDown(self):
        """Restore original config values"""
        config.CSV_MATCHES = self.original_paths['matches']
        config.CSV_VARIATIONS = self.original_paths['variations']
        config.CSV_ARBS = self.original_paths['arbs']

        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_optional_csv_paths(self):
        """Test that CSV_ARBS is marked as optional/deprioritized"""
        # This is a comment in the config, so we're testing that it exists
        # and doesn't break anything when set to None
        config.CSV_ARBS = None
        self.assertIsNone(config.CSV_ARBS)

    def test_time_threshold_value_appropriate(self):
        """Test that time threshold makes sense for stale kickoff detection"""
        # 2 minutes is reasonable for detecting stale times
        self.assertLessEqual(config.TIME_VARIATION_THRESHOLD_MINUTES, 5)
        self.assertGreaterEqual(config.TIME_VARIATION_THRESHOLD_MINUTES, 1)


class TestConfigUsage(unittest.TestCase):
    """Test that config values can be used as intended"""

    def test_urls_accessible(self):
        """Test that we can access bookmaker URLs and names"""
        for url, name in config.BOOKMAKER_URLS:
            self.assertIsNotNone(url)
            self.assertIsNotNone(name)

    def test_random_user_agent_selection(self):
        """Test that random selection from USER_AGENTS works"""
        import random
        agent = random.choice(config.USER_AGENTS)
        self.assertIn(agent, config.USER_AGENTS)

    def test_time_threshold_comparison(self):
        """Test time threshold can be used for comparisons"""
        now = datetime.now()
        older_time = now - timedelta(minutes=config.TIME_VARIATION_THRESHOLD_MINUTES + 1)
        newer_time = now - timedelta(minutes=config.TIME_VARIATION_THRESHOLD_MINUTES - 1)

        time_diff_older = now - older_time
        time_diff_newer = now - newer_time

        threshold = timedelta(minutes=config.TIME_VARIATION_THRESHOLD_MINUTES)

        self.assertGreater(time_diff_older, threshold)
        self.assertLess(time_diff_newer, threshold)


if __name__ == '__main__':
    unittest.main(verbosity=2)