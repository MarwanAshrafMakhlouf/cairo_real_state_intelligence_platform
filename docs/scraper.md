# Scraper.py

Scrapes full property details from individual listing pages. Expects a links CSV as input (produced by the link harvester) and outputs a CSV of structured property data with checkpoint/resume support.

---

## Dependencies
- `curl_cffi` — HTTP requests with Chrome fingerprint impersonation
- `selenium` + `undetected_chromedriver` — browser fallback for bot-protected pages
- `BeautifulSoup` — HTML parsing
- `pandas` — data accumulation and CSV I/O
- All selectors, file paths, and field definitions are read from `config.yaml`

---

## SmartScraper

Two-stage fetcher. Tries `curl_cffi` first; falls back to Selenium if the response looks like a challenge page (too short, contains "humbucker" or "challenge"). Cookies from Selenium are carried back into the `curl_cffi` session for subsequent requests.

| Method | Description |
|---|---|
| `get_html(url)` | Main entry point. Returns raw HTML via whichever method works |
| `try_requests_first(url)` | Fast path. Returns `None` if response appears to be a bot challenge |
| `use_selenium_fallback(url)` | Launches Chrome, loads the page, returns page source |
| `get_realistic_headers()` | Returns headers that match a real Chrome/Windows browser |
| `format_url(slug)` | Prepends base URL unless the slug is already a full URL |
| `close()` | Quits the Selenium driver if one was opened |

---

## Extraction Functions

Each function takes `(config, page_data, soup)` and returns an updated `page_data` dict. Returns an empty dict on failure.

| Function | Extracts |
|---|---|
| `extract_basic_info` | Price, listing date, seller name |
| `highlights_extractor` | Bedrooms, bathrooms, area, property subtype |
| `details_extractor` | Payment method, floor level, and similar structured fields |
| `additional_features_extractor` | Amenities — sets `True` if listed on page, `False` if absent |

`standardize_date()` is called inside `extract_basic_info` to convert relative date strings ("3 days ago", "yesterday") to `MM-DD-YYYY`.

---

## Utilities

**`get_page_data(slug, scraper, config, max_retries=5)`**
Retry wrapper around `scrape_single_page`. Returns `None` after `max_retries` failures.

**`property_not_available(soup, config)`**
Returns `True` if the listing is marked sold or removed. These are still saved with `seller_name = "Sold/Unavailable"`.

**`save_checkpoint / load_checkpoint`**
Persist and read the last successfully processed index from `checkpoint.json`.

**`safe_append_to_csv(new_rows, config)`**
Handles schema drift — if a new batch introduces columns that don't exist in the CSV yet, it backfills them as `None` before appending.

---

## main()

Reads config and links CSV, resumes from checkpoint if one exists, then loops through all links. Accumulates rows in memory and flushes every 1,000 to CSV. Skipped links are written to a separate file. On crash or keyboard interrupt, flushes current batch and saves checkpoint before exiting.