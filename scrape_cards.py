import requests
import time
import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start_page = 17000

driver = webdriver.Firefox()
driver.get(f"https://www.houzz.co.uk/photos/query/exterior/p/{start_page}")
print("Loading web page...")
# WebDriverWait(driver, 1000000).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Newly Featured"]'))).click()

card_links = set()
if os.path.exists('card_links.json') and (os.path.getsize('card_links.json') > 0):
    with open('card_links.json', 'r') as f:
        card_links = set(json.load(f))

def save_soup(to_file=False):
    global card_links
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for card in soup.find_all("a", {"class": "hz-photo-card__ratio-box"}):
        tqdm.write(card.get('href'))
        card_links.add(card.get('href'))

    if to_file:
        with open('card_links.json', 'w') as f:
            s = json.dumps(list(card_links), indent=4, sort_keys=True)
            f.write(s)

scroll_height = driver.execute_script("return document.body.scrollHeight;")
goal = 24980
prev_pos = -20
i = 0
last_refresh = i
prev_count = len(card_links)
no_progress = 0
with tqdm(total=goal) as pbar:
    while len(card_links) < goal:
        driver.execute_script(f"window.scrollTo(0, {scroll_height}*{i});")
        current_pos = driver.execute_script(f"return window.scrollY;")
        if(abs(current_pos - prev_pos) < 10) or no_progress > 5 or (i - last_refresh > 200):
            no_progress = 0
            last_refresh = i
            driver.get(f"https://www.houzz.co.uk/photos/query/exterior/p/{start_page+i}")
            prev_pos = -20
            time.sleep(5)
        else:
            prev_pos = current_pos
            time.sleep(1)

        if (len(card_links) - prev_count) > 20:
            pbar.n = len(card_links)
            prev_count = len(card_links)
            save_soup(to_file=True)
            pbar.refresh()
            no_progress = 0
        elif len(card_links) == prev_count:
            no_progress += 1
        save_soup()
        i += 1
save_soup(to_file=True)
driver.close()
driver.quit()

    


