import requests
from bs4 import BeautifulSoup
import os
from ddgs import DDGS
import re

DATA_DIR = "data/"

def sanitize_filename(text):
    # subs all characters not in that list with an _
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', text)[:50]

def scrape_pages():
    with DDGS() as ddgs: # open as an instance and then close
        results = ddgs.text("what was the Jackson Browne guitar setup", max_results=3)
        for i, r in enumerate(results):
            print(r["title"], r["href"])

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
    scrape_pages()
