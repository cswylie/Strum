import requests
from bs4 import BeautifulSoup
import os
from ddgs import DDGS
import re

DATA_DIR = "data/"

def sanitize_filename(text):
    # subs all characters not in that list with an _
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', text)[:50]

def scrape_pages(query):
    with DDGS() as ddgs: # open as an instance and then close
        results = ddgs.text(query, max_results=6)
        for i, r in enumerate(results):
            url = r["href"]

            # Skip YouTube links
            if "youtube.com" in url or "youtu.be" in url:
                print(f"Skipping YouTube link: {url}")
                continue

            response = requests.get(url)

            if response.status_code != 200:
                print(f"Skipping {url} (status: {response.status_code})")
                continue

            print(r["title"], url)

            response = requests.get(r["href"])
            soup = BeautifulSoup(response.text, "html.parser")

            # insert a newline between the text of different HTML elements
            # and removes trailing and leading whitespaces 
            text = soup.get_text(separator="\n", strip=True)

            filename = sanitize_filename(r["title"]) or f"page_{i}"
            filepath = os.path.join(DATA_DIR, f"{filename}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    query = input("Enter you're search query: ")
    scrape_pages(query)
