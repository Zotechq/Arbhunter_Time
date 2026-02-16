# flashscore_api_final.py
import requests
from datetime import datetime, timedelta
from config import RAPIDAPI_KEY


class FlashscoreAPI:
    def __init__(self, rapidapi_key):
        self.base_url = "https://flashlive-sports.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "flashlive-sports.p.rapidapi.com"
        }

    def get_matches_by_day(self, day_offset=0, sport_id=1):
        """
        Get matches for a specific day
        day_offset: 0 = today, -1 = yesterday, 1 = tomorrow, etc.
        """
        endpoint = f"{self.base_url}/v1/events/list"

        querystring = {
            "sport_id": str(sport_id),
            "locale": "en_INT",
            "timezone": "3",
            "day": str(day_offset),
            "indent_days": "1"
        }

        day_names = {
            "-1": "yesterday",
            "0": "today",
            "1": "tomorrow"
        }
        day_name = day_names.get(str(day_offset), f"day {day_offset}")

        print(f"\n📡 Fetching {day_name} matches (day={day_offset})...")

        try:
            response = requests.get(endpoint, headers=self.headers, params=querystring, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def parse_matches(self, api_response):
        """Parse matches from API response"""
        matches = []

        if not api_response or 'DATA' not in api_response:
            return matches

        for tournament in api_response['DATA']:
            league = tournament.get('NAME', 'Unknown League')

            for event in tournament.get('EVENTS', []):
                try:
                    home = event.get('HOME_NAME', 'Unknown')
                    away = event.get('AWAY_NAME', 'Unknown')

                    start_time = event.get('START_UTIME')
                    if start_time:
                        match_time = datetime.fromtimestamp(int(start_time))
                        kickoff = match_time.strftime('%H:%M')
                        date = match_time.strftime('%d/%m')
                    else:
                        kickoff = 'Unknown'
                        date = 'Unknown'

                    if home != 'Unknown' and away != 'Unknown':
                        matches.append({
                            'home': home,
                            'away': away,
                            'kickoff': kickoff,
                            'date': date,
                            'league': league,
                            'bookie': 'Flashscore (API)'
                        })

                except Exception:
                    continue

        return matches

    def get_formatted_matches(self, day_offset=0, sport_id=1):
        """Get matches in our standard format"""
        response = self.get_matches_by_day(day_offset, sport_id)
        if response:
            return self.parse_matches(response)
        return []


def test_api_days():
    """Test different day offsets"""

    print("=" * 70)
    print("🔍 TESTING FLASHSCORE API DAY OFFSETS")
    print("=" * 70)

    api = FlashscoreAPI(RAPIDAPI_KEY)

    # Test yesterday
    yesterday = api.get_formatted_matches(day_offset=-1)
    print(f"\n📅 Yesterday: {len(yesterday)} matches")

    # Test today
    today = api.get_formatted_matches(day_offset=0)
    print(f"📅 Today: {len(today)} matches")

    # Test tomorrow
    tomorrow = api.get_formatted_matches(day_offset=1)
    print(f"📅 Tomorrow: {len(tomorrow)} matches")

    # Show sample from each
    if today:
        print("\n📋 TODAY'S MATCHES (first 5):")
        for match in today[:5]:
            print(f"   {match['home'][:25]:25} vs {match['away'][:25]:25} @ {match['kickoff']} [{match['date']}]")

    return today


# Update the wrapper function
def get_flashscore_matches():
    """
    Wrapper that returns TODAY'S matches
    """
    api = FlashscoreAPI(RAPIDAPI_KEY)
    # Try day_offset=0 first, if empty try -1
    matches = api.get_formatted_matches(day_offset=0)
    if not matches:
        print("⚠️ No matches for day=0, trying day=-1...")
        matches = api.get_formatted_matches(day_offset=-1)
    return matches


if __name__ == "__main__":
    test_api_days()