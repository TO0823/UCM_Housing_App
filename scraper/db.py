"""Open the SQLite database, create tables from schema.sql, insert/update listings,
record a price-history row every run."""
import sqlite3
from pathlib import Path
from scraper.models import Listing

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def connect(db_path):
    conn = sqlite3.connect(db_path)             # the path that was passed in
    conn.execute("PRAGMA foreign_keys = ON")
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)                        # the method that runs a whole multi-statement .sql file
    conn.commit()
    return conn

def upsert_listing(conn, listing):
    """Insert or update a listing in the database."""
    row = conn.execute(
        """
        INSERT INTO listings (price, url, source, source_id, beds, baths, address, lat, lon, lease_length, posted_at, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, source_id) DO UPDATE SET
            price = excluded.price,
            url = excluded.url,
            beds = excluded.beds,
            baths = excluded.baths,
            address = excluded.address,
            lat = excluded.lat,
            lon = excluded.lon,
            lease_length = excluded.lease_length,
            posted_at = excluded.posted_at,
            image_url = excluded.image_url
        RETURNING id
        """,
        (
            listing.price, 
            listing.url, 
            listing.source, 
            listing.source_id, 
            listing.beds, 
            listing.baths, 
            listing.address, 
            listing.lat, 
            listing.lon, 
            listing.lease_length, 
            listing.posted_at.isoformat() if listing.posted_at is not None else None,
            listing.image_url
            )
    ).fetchone()

    return row[0]  # Return the row ID of the inserted/updated listing

def add_price(conn, listing_id, price):
    conn.execute(
        "INSERT INTO price_history (listing_id, price) VALUES (?, ?)",
        (listing_id, price)
    )