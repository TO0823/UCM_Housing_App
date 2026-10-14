
import pytest
from unittest.mock import patch, Mock
from scraper.routes import driving_route


def test_driving_route():
    # Simulate Google's API response.
    fake_response = Mock()

    fake_response.json.return_value = {
        "routes": [
            {
                "distanceMeters": 8883,
                "duration": "720s"
            }
        ]
    }

    with patch.dict(
        "os.environ",
        {"GOOGLE_MAPS_API_KEY": "fake_test_key"}
    ):
        with patch("scraper.routes.requests.post") as mock_post:
            mock_post.return_value = fake_response

            miles, minutes = driving_route(
                "3786 Horizons Ave, Merced, CA 95348"
            )

    assert miles == pytest.approx(5.52, abs=0.01)
    assert minutes == pytest.approx(12.0)

    mock_post.assert_called_once()


def test_missing_api_key():
    with patch.dict(
        "os.environ",
        {"GOOGLE_MAPS_API_KEY": ""},
    ):
        with pytest.raises(ValueError, match="GOOGLE_MAPS_API_KEY"):
            driving_route("3786 Horizons Ave, Merced, CA")


from scraper.db import connect
from scraper.models import Listing


def test_unique_addresses_from_database(tmp_path):
    conn = connect(tmp_path / "test.db")

    from scraper.db import upsert_listing

    for source_id, beds in [("1bed", 1), ("2bed", 2)]:
        upsert_listing(
            conn,
            Listing(
                price=1200,
                beds=beds,
                url="https://example.com",
                source="test",
                source_id=source_id,
                address="3786 Horizons Ave, Merced, CA 95348",
            )
        )

    conn.commit()

    rows = conn.execute(
        """
        SELECT DISTINCT address
        FROM listings
        WHERE address IS NOT NULL
          AND TRIM(address) != ''
        """
    ).fetchall()

    assert len(rows) == 1

    conn.close()