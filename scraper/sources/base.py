"""BaseScraper: opens a Playwright browser, defines scrape() -> list[Listing].
Each source subclasses this and only writes the part that is site-specific."""

import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from scraper.models import Listing

load_dotenv()


class BaseScraper:
    source: str = ""
    url: str = ""

    def scrape(self) -> list[Listing]:
        with sync_playwright() as playwright:

            browser_path = os.getenv("BROWSER_PATH")
            print("Selected browser:", browser_path or "Default Chromium")

            # NOTE (2026-10-17): headless mode is controlled by HEADLESS in .env instead of
            # being hard-coded. The default is a VISIBLE window because Apartments.com's bot
            # protection (Akamai) returns "Access Denied" to a headless browser; tested with
            # a real user agent and the automation flag disabled, still blocked. Visible mode
            # works (59 listings). Set HEADLESS=true to try headless again later. For the
            # scheduled job this means Task Scheduler must run it "only when user is logged on".
            headless = os.getenv("HEADLESS", "false").strip().lower() in ("true", "1", "yes")

            browser = playwright.chromium.launch(
                executable_path=browser_path or None,
                headless=headless
            )

            try:
                page = browser.new_page()
                page.goto(self.url, wait_until="domcontentloaded")

                return self.fetch(page)

            finally:
                browser.close()

    def fetch(self, page) -> list[Listing]:
        raise NotImplementedError