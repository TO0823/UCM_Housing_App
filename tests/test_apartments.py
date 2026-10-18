from pathlib import Path
from scraper.sources.apartments import ApartmentsScraper


def test_merced_horizons():
    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "merced_horizons.html"
    )

    html = fixture_path.read_text(encoding="utf-8")

    scraper = ApartmentsScraper()
    listings = scraper.parse_cards(html)

    assert len(listings) == 3

    assert [listing.price for listing in listings] == [
        1758, 1995, 2280
    ]

    assert [listing.beds for listing in listings] == [
        1, 2, 3
    ]

    assert all(
        listing.source == "apartments"
        for listing in listings
    )

    assert len({listing.source_id for listing in listings}) == 3


def test_total_pages():
    fixture_path = Path(__file__).parent / "fixtures" / "apartments_list_page.html"
    html = fixture_path.read_text(encoding="utf-8")

    scraper = ApartmentsScraper()

    assert scraper.total_pages(html) == 3
    assert scraper.total_pages("no pager here") == 1


def test_basic_house():
    fixture_path = Path(__file__).parent / "fixtures" / "basic_house.html"
    html = fixture_path.read_text(encoding="utf-8")

    scraper = ApartmentsScraper()
    listings = scraper.parse_cards(html)

    assert len(listings) == 1

    house = listings[0]

    assert house.source_id == "rttyzr1"
    assert "218 Shafer Ave" in house.address
    assert house.price == 2195
    assert house.beds == 5
    assert house.baths == 2.5
