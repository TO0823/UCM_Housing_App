
from unittest.mock import patch

from scraper.commutes import get_commutes, get_addresses_from_db
from scraper.db import connect, upsert_listing
from scraper.models import Listing
def test_duplicate_addresses():
    addresses = [
        "3786 Horizons Ave, Merced, CA 95348",
        "3786 Horizons Ave, Merced, CA 95348",
        "Another Property, Merced, CA",
    ]

    with patch(
        "scraper.commutes.driving_route",
        return_value=(5.52, 12.0)
    ) as mock_route:
        results = get_commutes(addresses)

    assert len(results) == 2
    assert mock_route.call_count == 2

    assert results[
        "3786 Horizons Ave, Merced, CA 95348"
    ] == (5.52, 12.0)



def test_get_addresses_from_db(tmp_path):
    conn = connect(tmp_path / "test.db")

    try:
        for source_id in ["1bed", "2bed"]:
            upsert_listing(
                conn,
                Listing(
                    price=1200,
                    url="https://example.com",
                    source="test",
                    source_id=source_id,
                    address="3786 Horizons Ave, Merced, CA 95348",
                )
            )

        conn.commit()

        addresses = get_addresses_from_db(conn)

        assert addresses == [
            "3786 Horizons Ave, Merced, CA 95348"
        ]

    finally:
        conn.close()