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

            browser = playwright.chromium.launch(
                executable_path=browser_path or None,
                headless=False
            )

            try:
                page = browser.new_page()
                page.goto(self.url, wait_until="domcontentloaded")

                return self.fetch(page)

            finally:
                browser.close()

    def fetch(self, page) -> list[Listing]:
        raise NotImplementedError