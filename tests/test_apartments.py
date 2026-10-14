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