# flashscore_scraper.py - WITH TIMEZONE CONVERSION
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import re
import json


def convert_to_kenya_time(time_str):
    """
    Convert time from GMT to Kenya time (GMT+3)
    If time is 10:00 GMT, returns 13:00 EAT
    """
    try:
        # Remove any non-time characters (like "FRO" suffix)
        clean_time = re.sub(r'[^0-9:]', '', time_str)
        time_obj = datetime.strptime(clean_time, '%H:%M')
        kenya_time = time_obj + timedelta(hours=3)
        return kenya_time.strftime('%H:%M')
    except:
        return time_str


def fetch_flashscore_matches(headless=True):
    """
    Fetch football matches from Flashscore Kenya and convert to Kenya time
    """
    print("=" * 70)
    print("⚽ FETCHING FLASHSCORE KENYA FOOTBALL MATCHES")
    print("=" * 70)

    options = Options()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(options=options)
    matches = []

    try:
        url = "https://www.flashscore.co.ke/"
        print(f"\n📡 Loading Flashscore Kenya...")
        driver.get(url)
        time.sleep(8)

        # Handle cookie consent
        try:
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
            cookie_btn.click()
            print("✅ Accepted cookies")
            time.sleep(2)
        except:
            pass

        # Navigate to football section
        try:
            football_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Football')]")
            football_link.click()
            print("✅ Clicked on Football")
            time.sleep(3)
        except:
            pass

        # Click on "Today" tab
        try:
            today_tab = driver.find_element(By.XPATH, "//*[contains(text(), 'TODAY')]")
            today_tab.click()
            print("✅ Clicked on TODAY tab")
            time.sleep(3)
        except:
            pass

        # Scroll to load more matches
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Get page source and parse
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all match elements
        match_elements = soup.find_all('div', class_=re.compile(r'event__match'))
        print(f"\n📦 Found {len(match_elements)} match elements")

        today_date = datetime.now().strftime('%d/%m')

        for match in match_elements:
            try:
                # Extract time
                time_elem = match.find('div', class_=re.compile(r'event__time'))
                if not time_elem:
                    continue
                gmt_time = time_elem.text.strip()

                # CONVERT TO KENYA TIME
                kenya_time = convert_to_kenya_time(gmt_time)

                # Extract home team
                home_elem = match.find('div', class_=re.compile(r'event__homeParticipant'))
                home = home_elem.text.strip() if home_elem else "Unknown"

                # Extract away team
                away_elem = match.find('div', class_=re.compile(r'event__awayParticipant'))
                away = away_elem.text.strip() if away_elem else "Unknown"

                # Extract league/tournament
                league_elem = match.find_previous('div', class_=re.compile(r'tournament__header'))
                league = league_elem.text.strip() if league_elem else "Football"

                if home != "Unknown" and away != "Unknown" and kenya_time:
                    match_data = {
                        'home': home,
                        'away': away,
                        'kickoff': kenya_time,  # NOW IN KENYA TIME
                        'original_gmt': gmt_time,  # For reference
                        'date': today_date,
                        'league': league,
                        'bookie': 'Flashscore'
                    }
                    matches.append(match_data)
                    print(f"✅ {home:30} vs {away:30} @ {kenya_time} [{today_date}] (was {gmt_time} GMT)")

            except Exception as e:
                continue

        print(f"\n📊 Total matches found: {len(matches)}")
        return matches

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        driver.quit()


def get_flashscore_matches():
    """Wrapper function for main system"""
    return fetch_flashscore_matches(headless=True)


if __name__ == "__main__":
    matches = fetch_flashscore_matches(headless=False)
    if matches:
        print(f"\n✅ Found {len(matches)} matches")
    else:
        print("\n❌ No matches found")