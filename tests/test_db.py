"""Tests: tables get created, inserting the same listing twice does not duplicate it,
every run adds a price_history row."""

from scraper.db import connect, upsert_listing, add_price
from scraper.models import Listing
from datetime import datetime

def test_db_tables(tmp_path):
    conn = connect(tmp_path / "test.db")

    rows = conn.execute(
        "SELECT name From sqlite_master WHERE type='table'"
        ).fetchall()
    
    names = [row[0] for row in rows]
    assert "listings" in names
    assert "price_history" in names
    assert "runs" in names

    conn.close()

def test_upsert_no_duplicates(tmp_path):
    conn = connect(tmp_path / "test.db")
    listing = Listing(price=1000, url="http://x", source="test", source_id="1")
    id1 = upsert_listing(conn, listing)
    id2 = upsert_listing(conn, listing)
    count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    assert count == 1
    assert id1 == id2


def test_add_price_grows_history(tmp_path):
    conn = connect(tmp_path / "test.db")
    listing = Listing(price=1000, url="http://x", source="test", source_id="1")
    listing_id = upsert_listing(conn, listing)
    add_price(conn, listing_id, 1000)
    add_price(conn, listing_id, 1100)
    count = conn.execute("SELECT COUNT(*) FROM price_history WHERE listing_id=?", (listing_id,)).fetchone()[0]
    assert count == 2
    last_seen = conn.execute(
        "SELECT last_seen FROM listings WHERE id=?",
        (listing_id,)
    ).fetchone()[0]

    newest_seen_at = conn.execute(
        """
        SELECT seen_at
        FROM price_history
        WHERE listing_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (listing_id,)
    ).fetchone()[0]

    assert last_seen == newest_seen_at

    conn.close()

def test_real_date_data(tmp_path):
    conn = connect(tmp_path / "test.db")
    listing = Listing(
        price=1500,
        url="http://example.com/listing/1",
        source="example",
        source_id="1",
        beds=2,
        baths=1.5,
        address="123 Main St",
        lat=37.7749,
        lon=-122.4194,
        lease_length="12 months",
        posted_at=datetime(2026, 10, 8, 14, 0),
        image_url="http://example.com/image.jpg"
    )
    listing_id = upsert_listing(conn, listing)
    add_price(conn, listing_id, 1500)

    # Verify that the listing was inserted correctly
    row = conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
    assert row is not None
    assert row[1] == 1500  # price
    assert row[2] == "http://example.com/listing/1"  # url
    assert row[3] == "example"  # source
    assert row[4] == "1"  # source_id

    saved_date = conn.execute(
        "SELECT posted_at FROM listings WHERE id=?",
        (listing_id,)
    ).fetchone()[0]

    assert saved_date.startswith("2026-10-08")

    conn.close()