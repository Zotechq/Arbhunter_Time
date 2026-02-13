import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from stem import Signal
from stem.control import Controller
import random
import time
import socks
import socket
from config import TOR_PROXY, CONTROL_PORT, CONTROL_PASSWORD, USER_AGENTS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, \
    IP_RENEW_EVERY_REQUESTS


def fetch_page(url, request_count, use_selenium=False):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    # 🔴 FORCE SELENIUM FOR ODIBETS (solves the empty page issue)
    if "odibets.com" in url:
        use_selenium = True
        print("  ⚡ Using Selenium for Odibets (JavaScript required)")

    if use_selenium:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={headers['User-Agent']}")

        try:
            # Try using Chrome first
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except:
            # Fall back to Firefox if Chrome fails
            print("  ⚠️ Chrome failed, trying Firefox...")
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument(f"user-agent={headers['User-Agent']}")
            driver = webdriver.Firefox(options=options)

        driver.get(url)
        # Wait longer for JavaScript to load matches
        time.sleep(random.uniform(8, 12))

        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        return soup
    else:
        # Regular requests for non-JS sites
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                print(f"Failed (code {response.status_code}) – Falling back to Selenium...")
                return fetch_page(url, request_count, use_selenium=True)
        except Exception as e:
            print(f"Error: {e} – Retrying after delay...")
            time.sleep(random.uniform(5, 10))
            return None