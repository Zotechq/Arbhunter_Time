from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get("https://www.odibets.com/sports/soccer")
time.sleep(8)  # Wait for dynamic content

# Save page source to inspect
with open("odibets_debug.html", "w") as f:
    f.write(driver.page_source)

print("Page saved. Check odibets_debug.html for match elements.")
driver.quit()