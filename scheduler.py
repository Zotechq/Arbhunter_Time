# scheduler.py - FINAL VERSION
from datetime import datetime, timedelta
import random


class DynamicScheduler:
    """
    Complete smart scheduler with time-based intervals, priority, jitter, and backoff
    """

    def __init__(self):
        self.base_intervals = {
            'far': 120,  # > 24 hours: every 2 hours
            'near': 30,  # 6-24 hours: every 30 mins
            'close': 15,  # 2-6 hours: every 15 mins
            'very_close': 5,  # 30-120 minutes: every 5 mins
            'critical': 2,  # < 30 minutes: every 2 mins
        }

        # Priority multipliers
        self.priority_multipliers = {
            'high': 0.7,
            'medium': 1.0,
            'low': 1.5,
        }

        # Popular leagues
        self.high_priority_leagues = [
            'Premier League', 'LaLiga', 'Bundesliga',
            'Serie A', 'Ligue 1', 'Champions League',
            'Europa League', 'World Cup', 'Euro'
        ]

        self.medium_priority_leagues = [
            'Championship', 'FA Cup', 'Carabao Cup',
            'Primeira Liga', 'Eredivisie', 'Super Lig'
        ]

        # Tracking
        self.last_scrape = {}
        self.domain_failures = {}
        self.domain_backoff = {}

        print("✅ DynamicScheduler initialized")

    def parse_match_datetime(self, date_str, time_str):
        """Convert match date/time to minutes until kickoff"""
        try:
            day, month = map(int, date_str.split('/'))
            hour, minute = map(int, time_str.split(':'))

            now = datetime.now()
            match_time = datetime(now.year, month, day, hour, minute)

            if match_time < now:
                match_time = match_time.replace(year=now.year + 1)

            diff = match_time - now
            return max(0, diff.total_seconds() / 60)
        except:
            return 1440  # Default 24 hours

    def get_league_priority(self, league):
        """Determine priority based on league name"""
        league_lower = league.lower()

        for high in self.high_priority_leagues:
            if high.lower() in league_lower:
                return 'high'

        for medium in self.medium_priority_leagues:
            if medium.lower() in league_lower:
                return 'medium'

        return 'low'

    def get_time_category(self, minutes_until):
        """Categorize how far away a match is"""
        if minutes_until > 1440:
            return 'far'
        elif minutes_until > 360:
            return 'near'
        elif minutes_until > 120:
            return 'close'
        elif minutes_until > 30:
            return 'very_close'
        else:
            return 'critical'

    def add_jitter(self, interval, jitter_percent=0.2):
        """Add random variation to interval"""
        jitter = random.uniform(-jitter_percent, jitter_percent)
        return max(1, interval * (1 + jitter))

    def get_interval(self, minutes_until, league="Football", domain=None):
        """Get scraping interval for a match"""
        base = self.base_intervals[self.get_time_category(minutes_until)]

        priority = self.get_league_priority(league)
        multiplier = self.priority_multipliers[priority]
        adjusted = base * multiplier

        if domain and domain in self.domain_backoff:
            adjusted += self.domain_backoff[domain]

        return self.add_jitter(adjusted)

    def record_failure(self, domain):
        """Record a failure for exponential backoff"""
        if domain not in self.domain_failures:
            self.domain_failures[domain] = 1
        else:
            self.domain_failures[domain] += 1

        failures = self.domain_failures[domain]
        backoff = min(5 * (2 ** (failures - 1)), 120)
        self.domain_backoff[domain] = backoff

        print(f"⚠️ {domain}: Failure #{failures}, backoff {backoff} mins")
        return backoff

    def record_success(self, domain):
        """Record a success to reduce backoff"""
        if domain in self.domain_failures:
            self.domain_failures[domain] = max(0, self.domain_failures[domain] - 1)

            if self.domain_failures[domain] == 0:
                if domain in self.domain_backoff:
                    del self.domain_backoff[domain]
                print(f"✅ {domain}: Fully recovered")
            else:
                failures = self.domain_failures[domain]
                backoff = min(5 * (2 ** (failures - 1)), 120)
                self.domain_backoff[domain] = backoff
                print(f"✅ {domain}: Improving, backoff now {backoff} mins")

    def generate_match_key(self, home, away, date):
        """Create unique match identifier"""
        return f"{home}_{away}_{date}".replace(" ", "_")

    def should_scrape(self, match_key, minutes_until, league="Football", domain=None):
        """Determine if a match should be scraped now"""
        interval = self.get_interval(minutes_until, league, domain)

        if match_key not in self.last_scrape:
            self.last_scrape[match_key] = datetime.now()
            return True, interval

        last = self.last_scrape[match_key]
        minutes_since = (datetime.now() - last).total_seconds() / 60

        if minutes_since >= interval:
            self.last_scrape[match_key] = datetime.now()
            return True, interval
        else:
            return False, interval - minutes_since

    def get_next_run_times(self, matches_by_source):
        """
        Generate report of when each match will be scraped next
        """
        report = {}

        for source, matches in matches_by_source.items():
            source_times = []
            for match in matches:
                key = self.generate_match_key(match['home'], match['away'], match['date'])
                minutes = self.parse_match_datetime(match['date'], match['kickoff'])
                league = match.get('league', 'Football')

                if key in self.last_scrape:
                    last = self.last_scrape[key]
                    interval = self.get_interval(minutes, league, source)
                    next_run = last + timedelta(minutes=interval)
                    source_times.append({
                        'match': f"{match['home']} vs {match['away']}",
                        'next_scrape': next_run.strftime('%H:%M:%S'),
                        'interval': f"{interval:.1f} mins"
                    })

            report[source] = source_times[:5]  # Top 5 matches

        return report


# Quick test
if __name__ == "__main__":
    scheduler = DynamicScheduler()

    print("\n📊 Testing complete scheduler:")

    # Simulate a real match
    match = {
        'home': 'Man United',
        'away': 'Liverpool',
        'date': '20/02',
        'kickoff': '17:30',
        'league': 'Premier League'
    }

    minutes = scheduler.parse_match_datetime(match['date'], match['kickoff'])
    key = scheduler.generate_match_key(match['home'], match['away'], match['date'])

    print(f"\n⚽ Match: {match['home']} vs {match['away']}")
    print(f"   Kickoff in: {minutes:.0f} mins")
    print(f"   Priority: {scheduler.get_league_priority(match['league'])}")

    # Test scraping decision
    should, next_in = scheduler.should_scrape(key, minutes, match['league'], "Odibets")
    print(f"\n🔍 First scrape decision: should_scrape={should}, next_in={next_in:.1f} mins")

    # Simulate waiting and checking again
    print("\n⏳ Simulating 10 minutes passing...")
    import time

    time.sleep(2)  # Just for demo
    should, next_in = scheduler.should_scrape(key, minutes - 10, match['league'], "Odibets")
    print(f"   After 10 mins: should_scrape={should}, next_in={next_in:.1f} mins")

    # Test failure handling
    print("\n🔴 Simulating failure...")
    scheduler.record_failure("Odibets")
    should, next_in = scheduler.should_scrape(key, minutes, match['league'], "Odibets")
    print(f"   After failure: interval increased, next_in={next_in:.1f} mins")