import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional
import time

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: str
    fetched_at: str

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
    response.encoding = "utf-8"
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Response size: {len(response.text)} characters")
    time.sleep(0.5)  
    return response.text

def extract_book_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for article in soup.select("article.product_pod h3 a"):
        href = article["href"]
        absolute_url = urljoin(page_url, href)
        links.append(absolute_url)
    return links

def find_next_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link:
        return urljoin(page_url, next_link["href"])
    return None

def discover_all_book_links():
    all_links = []
    link_sources = {}  # link -> source page mapping
    current_url = CATALOGUE_URL
    page_num = 1
    MAX_PAGES = 3

    while current_url and page_num <= MAX_PAGES:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html = fetch_page(current_url, cache_path)
        
        links = extract_book_links(html, current_url)
        for link in links:
            if link not in link_sources:
                link_sources[link] = current_url   
        all_links.extend(links)
        
        next_url = find_next_page(html, current_url)
        
        if page_num < MAX_PAGES and next_url:
            time.sleep(0.5)
        
        current_url = next_url
        page_num += 1
    
    unique_links = list(dict.fromkeys(all_links))
    
    print(f"catalogue_pages={min(page_num - 1, MAX_PAGES)}")
    print(f"discovered={len(all_links)}")
    print(f"unique_urls={len(unique_links)}")
    
    return unique_links, link_sources   

def extract_book_details(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")
    
    title = soup.select_one("div.product_main h1").get_text(strip=True)
    
    price_text = soup.select_one("p.price_color").get_text(strip=True)
    
    availability_text = soup.select_one("p.instock.availability").get_text(strip=True)
    
    rating_tag = soup.select_one("p.star-rating")
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        for c in classes:
            if c != "star-rating":
                rating_text = c

    description_tag = soup.select_one("#product_description")
    if description_tag:
        description = description_tag.find_next_sibling("p").get_text(strip=True)
    else:
        description = None
    
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

def scrape_all_books(book_links, link_sources):
    all_records = []
    for i, url in enumerate(book_links, start=1):
        cache_path = f"cache/book-{i}.html"
        html = fetch_page(url, cache_path)
        source_page = link_sources.get(url, "unknown")
        record = extract_book_details(html, url, source_page)
        all_records.append(record)
    
    print(f"detail_pages={len(all_records)}")
    return all_records

def parse_price(price_text):
    # Remove the £ symbol and commas, then convert the value to a float
    cleaned = price_text.replace("£", "").replace(",", "").strip()
    return float(cleaned)

def normalize_and_validate(raw_records):
    valid_records = []
    errors = []
    seen_urls = set()  # duplicate check 
    
    for raw in raw_records:
        try:
            # For the duplicate check - if this URL has already been seen, skip it.
            if raw["product_url"] in seen_urls:
                continue
            seen_urls.add(raw["product_url"])
            
            price_gbp = parse_price(raw["price_text"])
            
            record = BookRecord(
                title=raw["title"],
                product_url=raw["product_url"],
                price_text=raw["price_text"],
                price_gbp=price_gbp,
                availability_text=raw["availability_text"],
                rating_text=raw["rating_text"],
                description=raw["description"],
                source_page=raw["source_page"],
                fetched_at=raw["fetched_at"],
            )
            valid_records.append(record.model_dump())
        
        except (ValidationError, ValueError) as e:
            errors.append({"record": raw, "reason": str(e)})
    
    return valid_records, errors

def save_output(valid_records, errors):
    os.makedirs("output", exist_ok=True)
    
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
    
    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)
    
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")


if __name__ == "__main__":
    links, link_sources = discover_all_book_links()
    records = scrape_all_books(links, link_sources)
    valid_records, errors = normalize_and_validate(records)
    save_output(valid_records, errors)
