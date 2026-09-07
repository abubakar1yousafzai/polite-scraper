# The Polite Scraper

A small, polite scraping pipeline that downloads the first three catalogue pages of
[Books to Scrape](https://books.toscrape.com), visits all 60 book pages, and turns the
raw HTML into clean, schema-validated JSON records — without crashing on a broken page,
and with an honest report at the end of every run.

Built as part of the FlyRank Backend AI Engineering internship (Week 5 — Assignment A9).

## Target Classification

**Site:** Books to Scrape — https://books.toscrape.com

**Why this site:** Books to Scrape is a public sandbox built explicitly for practising
web scraping. It contains no real products, prices, or personal data — it exists for
exactly this purpose, which is why it is the only kind of site this assignment touches.

**Scope:** Only the first 3 catalogue pages (`page-1.html` to `page-3.html`), which
together list 60 books. This scraper visits those 60 book detail pages to extract data
— no other pages, categories, or site sections are accessed.

**robots.txt check:** Requested `https://books.toscrape.com/robots.txt` once — result:
no robots file found (404 response). A missing `robots.txt` is not the same as explicit
permission; it simply means the site has not published any crawling rules. Permission to
scrape here instead comes from the site's own description of itself as a scraping
practice sandbox.

**Data collected:** For each book — title, product URL, price, availability, star
rating, and description (when present). No personal data, accounts, or non-public
information is involved.

I will not reuse this code on another site without checking its rules and terms first.

## How to Install & Run

**Requirements:** Python 3.10+

1. Clone this repository and move into the scraper folder:
   ```bash
   git clone https://github.com/abubakar1yousafzai/polite-scraper
   cd polite-scraper
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   .venv\Scripts\activate
   uv pip install requests beautifulsoup4 pydantic
   ```
   *(or, without `uv`: `pip install requests beautifulsoup4 pydantic`)*

3. Run the scraper:
   ```bash
   python src/main.py
   ```

4. Output appears in:
   - `output/books.json` — 60 validated book records
   - `output/errors.json` — any records that failed schema validation
   - `output/run-report.json` — a summary of the run (see below)

   Subsequent runs read pages from `cache/` instead of re-requesting the site, and
   still produce exactly 60 records (idempotent — a rerun never duplicates data).

## Record Schema

Each validated record in `books.json` has this shape:

| Field                | Type            | Notes                                              |
|-----------------------|-----------------|-----------------------------------------------------|
| `title`               | string          | Book title                                          |
| `product_url`         | string          | Canonical (absolute) URL — the record's identity    |
| `price_text`          | string          | Raw price as shown on the page, e.g. `"£51.77"`     |
| `price_gbp`           | float           | Normalized numeric price, e.g. `51.77`              |
| `availability_text`   | string          | Raw availability text, e.g. `"In stock (22 available)"` |
| `rating_text`         | string \| null  | Star rating word, e.g. `"Three"`                    |
| `description`         | string \| null  | `null` when the book has no description — never invented |
| `source_page`         | string          | Which catalogue page (1–3) this book was found on   |
| `fetched_at`          | string          | UTC timestamp of when the record was fetched        |

Records are validated against this schema with Pydantic before being written. Any
record that fails validation is written to `errors.json` with the reason, and never
appears in `books.json`.

## Politeness Rules Followed

- **User-agent:** Every request identifies itself with a custom user-agent string
  naming this project, so a site owner could trace it back if needed.
- **Timeout:** Every request has a timeout — it never waits indefinitely for a response.
- **Delay:** The scraper waits at least 500ms between real requests to the site.
  Cached pages are read instantly, since they never leave the local machine.
- **Caching:** Every fetched page is saved to `cache/` and reused on subsequent runs,
  so the site is only hit once per page during development, not on every test run.
- **Status checks:** Only an HTTP `200` response is treated as a successful fetch;
  anything else is treated as a failure, not parsed as HTML.

## Surviving Failures

One broken page never brings down the whole run:

- Each book page is fetched inside its own error handler, so a single failure is
  logged and skipped rather than crashing the script.
- Timeouts and server errors (`5xx`) are retried once after a short wait.
  `404` and `403` responses are **not** retried, since retrying won't change the outcome.
- This was verified by deliberately adding one fake, non-existent book URL to the
  scrape list. The run still completed, `books.json` still contained the 60 real
  records, and `run-report.json` recorded the failure — see the sample report below.

### Sample `run-report.json`

```json
{
  "start_time": "2026-09-07T12:15:53.383093+00:00",
  "duration_seconds": 7.864935,
  "pages_fetched": 1,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed_page_details": [
    {
      "url": "https://books.toscrape.com/catalogue/this-book-does-not-exist/index.html",
      "reason": "Failed to fetch https://books.toscrape.com/catalogue/this-book-does-not-exist/index.html: status 404"
    }
  ]
}
```

## Why No Browser Was Needed

All the data this scraper collects — titles, prices, availability, ratings,
descriptions — is present directly in the server-rendered HTML of each page. Viewing
the page source (not just the rendered page) shows every value already there, with
nothing loaded afterward by JavaScript. A full browser (e.g. via Playwright) would only
add startup cost, memory usage, and complexity, with no additional data gained — a
plain HTTP request is sufficient and faster.

## Known Limitation

The "A Light in the Attic" book page contains duplicated text within its own
description paragraph in the site's raw HTML (verified via view-source, not introduced
by this scraper). This scraper stores the description exactly as received, per the
principle of never inventing or "cleaning" scraped content beyond what the assignment
calls for — the duplication is a property of the source data, not a bug in extraction.

## Ethics Note

This scraper only targets a site explicitly built for scraping practice, and only
collects the small, fixed slice of data (3 catalogue pages, 60 books) needed for this
assignment. In general: use an official API when one exists rather than scraping,
never bypass logins, paywalls, or explicit blocks, and collect only the data actually
needed rather than an entire site.

## Tech Stack

- Python 3.10+
- Requests (HTTP fetching)
- Beautiful Soup (HTML parsing)
- Pydantic (schema validation)
- Python's built-in `json` module (output)

## Project Structure

```
scraper/
├── src/
│   └── main.py          # fetch, extract, normalize, validate, store, report
├── cache/                # saved HTML pages (gitignored)
├── output/
│   ├── books.json        # 60 validated records
│   ├── errors.json       # any invalid records, with reasons
│   └── run-report.json   # summary of the last run
├── .gitignore
└── README.md
```