import requests
import time
import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

start_page = 1

driver = webdriver.Firefox(executable_path="C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver.get(f"https://www.houzz.co.uk/photos/phbr4-bp~t_10378~a_18-85-86-87-88?pg={start_page}")
print("Loading web page...")

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
goal = 25000
prev_pos = -20
i  = 0
while len(card_links) < goal:
    driver.execute_script(f"window.scrollTo(0, {scroll_height}*{i});")
    current_pos = driver.execute_script(f"return window.scrollY;")
    if(abs(current_pos - prev_pos) < 10):
        driver.get(f"https://www.houzz.co.uk/photos/phbr4-bp~t_10378~a_18-85-86-87-88?pg={start_page+i}")
        prev_pos = -20
        time.sleep(5)
    else:
        prev_pos = current_pos
        time.sleep(1)

    if (len(card_links) % 10) == 0:
        save_soup(to_file=True)
    else:
        save_soup()
    i += 1

    


