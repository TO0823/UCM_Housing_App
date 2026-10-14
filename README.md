# UCM Housing App

Hourly tracker of rental prices around UC Merced.

Parts:
- scraper/   Playwright scrapers that pull listings from Zillow, Apartments.com, Facebook Marketplace
- data/      SQLite database lives here (ignored by git)
- tests/     pytest tests
- docs/      design notes + mockups

Run once:   python -m scraper.main
Schedule:   see docs/scheduling.md

