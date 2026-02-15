# betika_selenium.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


def fetch_betika_with_selenium():
    """Fetch Betika matches using Selenium (headless)"""

    print("=" * 60)
    print("⚽ BETIKA MATCH EXTRACTOR WITH SELENIUM")
    print("=" * 60)

    # Set up Firefox options
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # Set a real user agent
    options.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0")

    print("🚀 Launching Firefox in headless mode...")
    driver = webdriver.Firefox(options=options)

    try:
        # Load the page
        print("🌐 Loading https://www.betika.com/en-ke/s/soccer...")
        driver.get("https://www.betika.com/en-ke/s/soccer")

        # Wait for matches to load (look for any match text)
        print("⏳ Waiting for matches to load...")
        time.sleep(10)  # Give it time to load

        # Try to wait for specific content
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sporting')]"))
            )
            print("✅ Match data detected!")
        except:
            print("⚠️ Timeout waiting for matches, but continuing...")

        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Get the page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Save HTML for inspection
        with open('betika_selenium.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("📄 Saved rendered HTML to 'betika_selenium.html'")

        # Extract matches
        matches = extract_betika_matches(soup)

        return matches

    finally:
        driver.quit()


def extract_betika_matches(soup):
    """Extract match data from Betika HTML"""

    matches = []

    # Get all text from the page
    page_text = soup.get_text()

    # Look for match patterns in the text
    # Pattern: League • League Name then Date/Time then Teams

    # Split into lines and process
    lines = page_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for date/time pattern (e.g., "16/02, 04:30")
        time_match = re.search(r'(\d{2}/\d{2}),?\s*(\d{2}:\d{2})', line)
        if time_match:
            date_str = time_match.group(1)
            time_str = time_match.group(2)

            # Look at next line for teams
            if i + 1 < len(lines):
                team_line = lines[i + 1].strip()

                # Try to split into two teams
                # Betika shows teams as "Sporting Fc Famalicao" (no "vs")
                # We need to split intelligently

                # Common team name patterns
                common_teams = ['Sporting', 'Famalicao', 'Botafogo', 'Flamengo',
                                'Gremio', 'Juventude', 'Colo Colo', 'Boca Juniors']

                # Find which teams appear in this line
                teams_found = []
                for team in common_teams:
                    if team.lower() in team_line.lower():
                        teams_found.append(team)

                if len(teams_found) >= 2:
                    home = teams_found[0]
                    away = teams_found[1]

                    match = {
                        'home': home,
                        'away': away,
                        'date': date_str,
                        'time': time_str,
                        'bookie': 'Betika'
                    }
                    matches.append(match)
                    print(f"✅ {home} vs {away} @ {date_str} {time_str}")

        i += 1

    return matches


def simple_test():
    """Simpler test to see what text we get"""

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://www.betika.com/en-ke/s/soccer")
        time.sleep(10)

        # Get all visible text
        body_text = driver.find_element(By.TAG_NAME, "body").text

        print("\n📝 First 1000 characters of page text:")
        print("-" * 40)
        print(body_text[:1000])
        print("-" * 40)

        # Look for match patterns
        print("\n🔍 Searching for match patterns...")

        # Look for "16/02, 04:30" patterns
        import re
        times = re.findall(r'\d{2}/\d{2},?\s*\d{2}:\d{2}', body_text)
        print(f"Found {len(times)} time patterns: {times[:10]}")

        # Look for team names
        teams = re.findall(r'(Sporting|Famalicao|Botafogo|Flamengo|Gremio|Juventude)', body_text)
        print(f"Found {len(teams)} team mentions: {list(set(teams))[:10]}")

    finally:
        driver.quit()


if __name__ == "__main__":
    print("🔍 SIMPLE TEST FIRST")
    print("=" * 60)
    simple_test()

    print("\n" + "=" * 60)
    print("📊 FULL EXTRACTION")
    print("=" * 60)
    matches = fetch_betika_with_selenium()

    print(f"\n📊 Total matches found: {len(matches)}")
    if matches:
        print("\n📋 Matches:")
        for match in matches[:10]:
            print(f"  {match['home']} vs {match['away']} @ {match['date']} {match['time']}")