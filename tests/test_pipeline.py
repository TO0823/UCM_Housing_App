from scraper.db import connect
from scraper.models import Listing
from scraper.pipeline import run_scraper
import pytest

class FakeScraper:
    source = "test"

    def scrape(self):
        return [
            Listing(
                price=1000,
                beds=1,
                url="https://example.com/1",
                source="test",
                source_id="1",
            ),
            Listing(
                price=1500,
                beds=2,
                url="https://example.com/2",
                source="test",
                source_id="2",
            ),
        ]


def test_pipeline_no_duplicates_but_history_grows(tmp_path):
    conn = connect(tmp_path / "test.db")
    scraper = FakeScraper()

    # First run
    run_scraper(conn, scraper)

    count = conn.execute(
        "SELECT COUNT(*) FROM listings"
    ).fetchone()[0]

    assert count == 2

    # Second run
    run_scraper(conn, scraper)

    listing_count = conn.execute(
        "SELECT COUNT(*) FROM listings"
    ).fetchone()[0]

    history_count = conn.execute(
        "SELECT COUNT(*) FROM price_history"
    ).fetchone()[0]

    assert listing_count == 2
    assert history_count == 4

    conn.close()


class FailingScraper:
    source = "test"

    def scrape(self):
        raise RuntimeError("Website failed to load")


def test_successful_run_recorded(tmp_path):
    conn = connect(tmp_path / "test.db")

    run_scraper(conn, FakeScraper())

    row = conn.execute(
        "SELECT source, listings_found, status FROM runs"
    ).fetchone()

    assert row == ("test", 2, "success")

    conn.close()


def test_failed_run_recorded(tmp_path):
    conn = connect(tmp_path / "test.db")

    with pytest.raises(RuntimeError):
        run_scraper(conn, FailingScraper())

    row = conn.execute(
        "SELECT source, listings_found, status FROM runs"
    ).fetchone()

    assert row == ("test", 0, "failed")

    conn.close()

def test_pipeline_rolls_back_on_failure(tmp_path):
    conn = connect(tmp_path / "test.db")

    class PartiallyFailingScraper:
        source = "test"

        def scrape(self):
            return [
                Listing(
                    price=1000,
                    url="https://example.com/1",
                    source="test",
                    source_id="1"
                ),
                Listing(
                    price=1500,
                    url="https://example.com/2",
                    source="test",
                    source_id="2"
                ),
            ]

    # Force a database error on the second price-history insert.
    conn.execute("""
        CREATE TRIGGER fail_second_listing
        BEFORE INSERT ON price_history
        WHEN NEW.price = 1500
        BEGIN
            SELECT RAISE(ABORT, 'Simulated failure');
        END;
    """)

    conn.commit()

    with pytest.raises(Exception, match="Simulated failure"):
        run_scraper(conn, PartiallyFailingScraper())

    listing_count = conn.execute(
        "SELECT COUNT(*) FROM listings"
    ).fetchone()[0]

    history_count = conn.execute(
        "SELECT COUNT(*) FROM price_history"
    ).fetchone()[0]

    run_status = conn.execute(
        "SELECT status FROM runs"
    ).fetchone()[0]

    assert listing_count == 0
    assert history_count == 0
    assert run_status == "failed"

    conn.close()