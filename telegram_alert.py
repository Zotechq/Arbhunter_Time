# telegram_alert.py - STEP 3: Working Version
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramAlert:
    """
    Telegram alert system for conflict notifications
    """

    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize with your bot token and chat ID
        """
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # Test connection on startup
        self.test_connection()

    def test_connection(self):
        """Test if the bot token is valid"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Telegram bot connected: @{bot_info['result']['username']}")
                return True
            else:
                print(f"❌ Telegram connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            return False

    def send_alert(self, conflict_data):
        """
        Send a formatted alert about a conflict
        """
        # Format the message
        message = self._format_conflict_message(conflict_data)

        # Send it
        return self.send_message(message)

    def send_message(self, message):
        """
        Send a text message to Telegram
        """
        url = f"{self.base_url}/sendMessage"

        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print("✅ Telegram alert sent")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                return False

        except Exception as e:
            print(f"❌ Telegram exception: {e}")
            return False

    def _format_conflict_message(self, conflict):
        """
        Format a conflict nicely for Telegram
        """
        lines = [
            "🚨 <b>KICKOFF TIME CONFLICT DETECTED!</b>",
            "",
            f"⚽ <b>{conflict['home']} vs {conflict['away']}</b>",
            f"🏆 League: {conflict.get('league', 'Unknown')}",
            f"📅 Date: {conflict.get('date', 'Unknown')}",
            "",
            "⏰ <b>Times:</b>"
        ]

        for source, time in conflict['times'].items():
            lines.append(f"   • {source}: {time}")

        lines.extend([
            "",
            f"⏱️ <i>Detected at: {conflict['timestamp'][:16]}</i>"
        ])

        return "\n".join(lines)

    def send_test_message(self):
        """Send a test message to verify everything works"""
        test_conflict = {
            'home': 'Manchester United',
            'away': 'Liverpool',
            'league': 'Premier League',
            'date': '20/02',
            'times': {
                'Flashscore': '17:30',
                'Betika': '20:30',
                'Odibets': '20:30'
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.send_alert(test_conflict)


# Simple test
if __name__ == "__main__":
    from datetime import datetime

    print("\n📊 Testing Telegram alert:")

    # Initialize the alert system
    alert = TelegramAlert()

    # Send a test message
    if alert.send_test_message():
        print("✅ Test successful! Check your Telegram")
    else:
        print("❌ Test failed")