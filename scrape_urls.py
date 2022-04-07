import grequests
import requests
import time
import shutil
import json
import os
from tqdm import tqdm
from functools import partial
from bs4 import BeautifulSoup
import argparse
parser = argparse.ArgumentParser("AAAAA")
parser.add_argument('--offset', type=int, default=0)
args = parser.parse_args()

offset = args.offset
if args.offset == 0:
    offset = max([int(f[:f.index('.')]) for f in os.listdir('./scraped/')]) + 1
print(offset)
card_urls = set()
if os.path.exists('card_links.json') and os.path.getsize('card_links.json') > 0:
    with open('card_links.json', 'r') as f:
            card_urls = set(json.load(f))

scraped_jpg_urls = set()
if os.path.exists('scraped.json') and os.path.getsize('scraped.json') > 0:
    with open('scraped.json', 'r') as f:
            scraped_jpg_urls = set(json.load(f))

reqs = (grequests.get(url) for url in card_urls)
pages = grequests.imap(reqs, size=16)
jpg_urls = set()
for page in tqdm(pages, total=len(card_urls)):
    soup = BeautifulSoup(page.content, 'html.parser')
    content = json.loads(soup.find('script', {'type': 'application/ld+json'}).decode_contents())
    jpg_urls.add(content[0]['contentURL'])
    tqdm.write(content[0]['contentURL'])

jpg_urls = jpg_urls - scraped_jpg_urls

reqs = (grequests.get(img_url, stream=True) for img_url in jpg_urls)
imgs = grequests.imap(reqs, size=16)

for i, r in enumerate(tqdm(imgs, total=len(jpg_urls))):    
    with open(f'./scraped.json', 'w') as scraped_file:    
        with open(f'./scraped/{(i + offset):05d}.jpg', 'wb') as f:
            for byte_chunk in r.iter_content(chunk_size=1024*10):
                if byte_chunk:
                    f.write(byte_chunk)
                    f.flush()
                    os.fsync(f)
        scraped_jpg_urls.add(r.url)
        scraped_file.write(json.dumps(list(scraped_jpg_urls), indent=4, sort_keys=True))
        