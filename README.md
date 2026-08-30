## Target classification

**Site:** Books to Scrape — https://books.toscrape.com

**Why this site:** Books to Scrape is a public sandbox built by ScrapingHub explicitly for practising web scraping. It contains no real products, prices, or personal data — it exists for exactly this purpose, which makes it the only kind of site this assignment touches.

**Scope:** Only the first 3 catalogue pages
(page-1.html, page-2.html, page-3.html), which together list 60 books.
This assignment visits those 60 book detail pages to extract data — no other
pages, categories, or site sections are accessed.

**robots.txt check:** Requested https://books.toscrape.com/robots.txt once —
result: no robots file found (404 response). A missing robots.txt file is not
the same as explicit permission; it simply means the site has not published any
crawling rules. Permission to scrape here instead comes from the site's own
description of itself as a scraping practice sandbox.

**Data collected:** For each book — title, product URL, price, availability,
star rating, and description (when present). No personal data, accounts, or
non-public information is involved.

**Why this is appropriate:** The target is a sandbox designed for this exact
use case, the scope is limited to a small, fixed slice of the site (3 pages,
60 books), and the scraper identifies itself honestly via its user-agent and
waits between requests.

I will not reuse this code on another site without checking its rules and terms first.