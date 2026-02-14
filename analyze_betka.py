from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def analyze_sportpesa():
    print("=" * 60)
    print("ANALYZING SPORTPESA STRUCTURE")
    print("=" * 60)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        # Try different possible SportPesa URLs
        urls_to_try = [
            "https://www.ke.sportpesa.com/en/sports-betting/football-1/"
        ]

        for url in urls_to_try:
            print(f"\n1. Trying {url}...")
            driver.get(url)
            time.sleep(8)

            # Save page source for this URL
            filename = f"sportpesa_debug_{urls_to_try.index(url)}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"✅ Saved {filename}")

            # Quick check if page loaded
            page_text = driver.page_source
            if "football" in page_text.lower() or "soccer" in page_text.lower():
                print(f"✅ Page seems to have football content")

                # Look for match containers
                from selenium.webdriver.common.by import By

                common_selectors = [
                    "div.event",
                    "div.match",
                    "div.fixture",
                    "div.game-row",
                    "div[class*='match']",
                    "div[class*='event']",
                    "div[class*='game']",
                    "tr",
                    "div.odds"
                ]

                print("\n2. Searching for match patterns...")
                for selector in common_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with '{selector}'")
                        if len(elements) > 0:
                            print(f"   Sample: {elements[0].text[:200]}\n")
            else:
                print(f"❌ No football content found at {url}")

    finally:
        driver.quit()


if __name__ == "__main__":
    analyze_sportpesa()