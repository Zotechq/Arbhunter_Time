# Central configurations for ArbHunter
from datetime import timedelta, datetime

BOOKMAKER_URLS = [  # List of (url, name) – replace with real pre-match odds pages (e.g., Bet365 football upcoming)
    ("https://www.odibets.com/sports/soccer", "Odibets"),
    ("https://www.mozzartbet.co.ke/en#/betting/?sid=1", "Mozzartbet"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.133 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Edg/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/129.0.0.0"
]

TOR_PROXY = "socks5://127.0.0.1:9050"
CONTROL_PORT = 9051
CONTROL_PASSWORD = None  # Set if configured in torrc
CSV_MATCHES = "matches.csv"
CSV_VARIATIONS = "matches_with_varying_times.csv"
CSV_ARBS = "sure_bets.csv"
MIN_TIME_BUFFER = timedelta(minutes=15)  # Pre-match filter
MIN_ARB_PCT = 1.2  # Minimum arb %
REFRESH_INTERVAL_MINUTES = 5  # Loop schedule
REQUEST_DELAY_MIN = 1
REQUEST_DELAY_MAX = 5
IP_RENEW_EVERY_REQUESTS = 5