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

urls = []
if os.path.exists('card_links.json') and os.path.getsize('card_links.json') > 0:
    with open('card_links.json', 'r') as f:
            urls = json.load(f)

scraped = set()
if os.path.exists('scraped.json') and os.path.getsize('scraped.json') > 0:
    with open('scraped.json', 'r') as f:
            scraped = set(json.load(f))

reqs = (grequests.get(url) for url in urls)
pages = grequests.imap(reqs, size=16)
img_urls = []
for page in tqdm(pages, total=len(urls)):
    soup = BeautifulSoup(page.content, 'html.parser')
    content = json.loads(soup.find('script', {'type': 'application/ld+json'}).decode_contents())
    img_urls.append(content[0]['contentURL'])
    tqdm.write(content[0]['contentURL'])

img_urls = filter(lambda img_url: img_url not in scraped, img_urls)

reqs = (grequests.get(img_url, stream=True) for img_url in img_urls)
imgs = grequests.imap(reqs, size=16)

for i, r in enumerate(tqdm(imgs)):    
    with open(f'./scraped.json', 'w') as scraped_file:    
        with open(f'./scraped/{(i + args.offset):05d}.jpg', 'wb') as f:
            for byte_chunk in r.iter_content(chunk_size=1024*10):
                if byte_chunk:
                    f.write(byte_chunk)
                    f.flush()
                    os.fsync(f)
    scraped.add(r.url)
    scraped_file.write(json.dumps(list(scraped), indent=4, sort_keys=True))
        