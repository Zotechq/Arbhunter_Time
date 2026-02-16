# flashscore_api_working.py
import requests
from datetime import datetime
from config import RAPIDAPI_KEY


class FlashscoreAPI:
    def __init__(self, rapidapi_key):
        self.base_url = "https://flashlive-sports.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "flashlive-sports.p.rapidapi.com"
        }

    def get_today_matches(self, sport_id=1):
        """Get today's matches with all required parameters"""
        endpoint = f"{self.base_url}/v1/events/list"

        querystring = {
            "sport_id": str(sport_id),
            "locale": "en_INT",
            "timezone": "3",  # Kenya time (UTC+3)
            "day": "0",  # Today
            "indent_days": "1"
        }

        print(f"\n📡 Fetching matches from Flashscore API...")

        try:
            response = requests.get(endpoint, headers=self.headers, params=querystring, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None

    def parse_matches(self, api_response):
        """
        Parse matches from API response
        Based on actual response structure from debug
        """
        matches = []

        if not api_response or 'DATA' not in api_response:
            return matches

        for tournament in api_response['DATA']:
            league = tournament.get('NAME', 'Unknown League')

            for event in tournament.get('EVENTS', []):
                try:
                    # Extract team names - from debug we see these are the correct fields
                    home = event.get('HOME_NAME', 'Unknown')
                    away = event.get('AWAY_NAME', 'Unknown')

                    # Get start time (UTC timestamp)
                    start_time = event.get('START_UTIME')
                    if start_time:
                        # Convert to Kenya time (UTC+3)
                        match_time = datetime.fromtimestamp(int(start_time))
                        kickoff = match_time.strftime('%H:%M')
                        date = match_time.strftime('%d/%m')
                    else:
                        kickoff = 'Unknown'
                        date = 'Unknown'

                    # Only add if we have real team names
                    if home != 'Unknown' and away != 'Unknown' and home and away:
                        matches.append({
                            'home': home,
                            'away': away,
                            'kickoff': kickoff,
                            'date': date,
                            'league': league,
                            'bookie': 'Flashscore (API)'
                        })

                except Exception as e:
                    continue

        return matches

    def get_formatted_matches(self, sport_id=1):
        """
        Convenience method that returns matches in our standard format
        """
        response = self.get_today_matches(sport_id)
        if response:
            return self.parse_matches(response)
        return []


def test_api():
    """Test the working API"""

    print("=" * 70)
    print("⚽ FLASHSCORE API - WORKING VERSION")
    print("=" * 70)

    api = FlashscoreAPI(RAPIDAPI_KEY)
    matches = api.get_formatted_matches(sport_id=1)

    if matches:
        print(f"\n✅ Found {len(matches)} matches")

        print("\n📋 FIRST 20 MATCHES (Kenya Time):")
        print("-" * 80)
        for i, match in enumerate(matches[:20], 1):
            print(f"{i:2}. {match['home'][:25]:25} vs {match['away'][:25]:25} @ {match['kickoff']} [{match['date']}]")

        print(f"\n📊 Total matches available: {len(matches)}")
        return matches
    else:
        print("\n❌ No matches found")
        return []


# For integration with your main comparison system
def get_flashscore_matches():
    """
    Wrapper function that returns matches in the format expected by your main program
    """
    api = FlashscoreAPI(RAPIDAPI_KEY)
    return api.get_formatted_matches()


if __name__ == "__main__":
    matches = test_api()

    # Example of how to use in your main comparison
    if matches:
        print("\n📝 Ready for comparison:")
        for match in matches[:5]:
            print(f"   {match['home']} vs {match['away']} @ {match['kickoff']}")