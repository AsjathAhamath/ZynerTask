# YC Scraper

This project queries the Y Combinator Algolia index (20 results per page across 25 pages), extracts company name, batch, one-liner, and slug, then saves them to `yc_companies.csv` using pandas. Install `requests` and `pandas`, set a valid Algolia API key in `HEADERS` inside `.venv/YcScraperAssessment/YcScraper.py`, and run `python .venv/YcScraperAssessment/YcScraper.py` from the repo root.
