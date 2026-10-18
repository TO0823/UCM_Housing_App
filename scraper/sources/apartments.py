import re
from bs4 import BeautifulSoup

from scraper.sources.base import BaseScraper
from scraper.models import Listing
from scraper.parse import parse_price, parse_beds, parse_baths


class ApartmentsScraper(BaseScraper):
    source = "apartments"
    BB = "lt2rnh_rlOhk19wJ"
    url = f"https://www.apartments.com/?bb={BB}"

    def parse_cards(self, html: str) -> list[Listing]:
        soup = BeautifulSoup(html, "html.parser")
        listings = []

        cards = soup.select("article.placard[data-listingid]")

        for card in cards:
            property_id = card.get("data-listingid")

            link = card.select_one("a.property-link")
            address = (
                card.select_one(".property-address")
                or card.select_one(".property-title")
            )
            image = card.select_one("img.js-placard-photo")

            if not property_id or not link:
                continue

            url = link.get("href")
            if not url:
                continue

            address_text = (
                address.get_text(strip=True)
                if address else None
            )
            image_url = image.get("src") if image else None

            plan_rows = card.select(".bedRentBox")

            if plan_rows:
                # COMPLEX CARDS
                for plan in plan_rows:
                    price_element = plan.select_one(".priceTextBox")
                    beds_element = plan.select_one(".bedTextBox")

                    if not price_element or not beds_element:
                        continue

                    price = parse_price(
                        price_element.get_text(strip=True)
                    )
                    beds = parse_beds(
                        beds_element.get_text(strip=True)
                    )

                    if price is None or beds is None:
                        continue

                    listing = Listing(
                        price=price,
                        beds=beds,
                        baths=None,
                        address=address_text,
                        lat=None,
                        lon=None,
                        lease_length=None,
                        posted_at=None,
                        url=url,
                        image_url=image_url,
                        source=self.source,
                        source_id=f"{property_id}-{beds}bed"
                    )

                    listings.append(listing)

            else:
                # BASIC CARDS (HOUSES)
                price_element = card.select_one(".property-pricing")
                beds_element = card.select_one(".bed-range")

                if not price_element or not beds_element:
                    continue

                price_text = price_element.get_text(" ", strip=True)
                beds_text = beds_element.get_text(" ", strip=True)

                price = parse_price(price_text)
                beds = parse_beds(beds_text)
                baths = parse_baths(beds_text)

                if price is None or beds is None:
                    continue

                listing = Listing(
                    price=price,
                    beds=beds,
                    baths=baths,
                    address=address_text,
                    lat=None,
                    lon=None,
                    lease_length=None,
                    posted_at=None,
                    url=url,
                    image_url=image_url,
                    source=self.source,
                    source_id=property_id
                )

                listings.append(listing)

        return listings

    def page_url(self, n):
        if n == 1:
            return self.url

        return f"https://www.apartments.com/{n}/?bb={self.BB}"

    def total_pages(self, html: str) -> int:
        match = re.search(r"Page \d+ of (\d+)", html)

        if match is None:
            return 1

        return int(match.group(1))

    def fetch(self, page) -> list[Listing]:
        # NOTE: this used to also save `html` to tests/fixtures/apartments_list_page.html
        # on every scrape. Removed 2026-10-17: it overwrote the test fixture every run and
        # crashed when the folder was missing. To capture a fresh fixture on purpose, run:
        #     python scratch/save_fixture.py

        # NOTE (2026-10-17): results are paginated, 40 cards per page. We stop by reading
        # "Page 1 of N" rather than waiting for an empty page, because asking for a page
        # past the end silently redirects back to page 1 and would loop forever.

        # PAGE 1 is already open: BaseScraper.scrape() navigated to self.url before
        # calling fetch(), so there is no goto here.
        page.wait_for_selector(
            "article.placard[data-listingid]",
            timeout=15000
        )

        html = page.content()
        listings = self.parse_cards(html)

        total = self.total_pages(html)

        print(f"Page 1: {len(listings)} listings")
        print(f"Total pages: {total}")

        # PAGE 2 THROUGH LAST PAGE
        for n in range(2, total + 1):
            page.goto(
                self.page_url(n),
                wait_until="domcontentloaded"
            )

            page.wait_for_selector(
                "article.placard[data-listingid]",
                timeout=15000
            )

            new_listings = self.parse_cards(page.content())

            listings.extend(new_listings)

            print(f"Page {n}: {len(new_listings)} listings")

            page.wait_for_timeout(2000)  # be polite between pages

        print(f"Total listings: {len(listings)}")

        return listings
