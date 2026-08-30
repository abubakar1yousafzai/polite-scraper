import requests
import os

CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_FILE = "cache/catalogue-page-1.html"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/abubakar1yousafzai/polite-scraper)"
TIMEOUT = 10  # seconds

def fetch_page(url, cache_path):
    if os.path.exists(cache_path):
        print(f"CACHE HIT: reading {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    
    print(f"FETCH: requesting {url}")
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Response size: {len(response.text)} characters")
    return response.text

if __name__ == "__main__":
    html = fetch_page(CATALOGUE_URL, CACHE_FILE)
    print(f"Total size: {len(html)} characters")