import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from stem import Signal
from stem.control import Controller
import random
import time
import socks
import socket
from config import TOR_PROXY, CONTROL_PORT, CONTROL_PASSWORD, USER_AGENTS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, \
    IP_RENEW_EVERY_REQUESTS

# Set global Tor proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket


def renew_tor_ip():
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate(password=CONTROL_PASSWORD)
        controller.signal(Signal.NEWNYM)
        print("Renewed Tor IP")


def fetch_page(url, request_count, use_selenium=False):
    if request_count % IP_RENEW_EVERY_REQUESTS == 0:
        renew_tor_ip()

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    if use_selenium:
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"user-agent={headers['User-Agent']}")
        options.add_argument('--proxy-server=' + TOR_PROXY)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(random.uniform(2, 4))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        return soup
    else:
        try:
            response = requests.get(url, headers=headers, proxies={"http": TOR_PROXY, "https": TOR_PROXY})
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                print(f"Failed (code {response.status_code}) – Falling back to Selenium...")
                return fetch_page(url, request_count, use_selenium=True)
        except Exception as e:
            print(f"Error: {e} – Retrying after delay...")
            time.sleep(random.uniform(5, 10))
            return None