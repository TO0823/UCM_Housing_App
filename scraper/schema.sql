-- Tables:
--   listings       one row per unique listing (source + source_id)
--   price_history  one row per listing per scrape run (listing_id, price, seen_at)
--   runs           one row per scraper run (started_at, source, listings_found, status)

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Required fields
    price INTEGER NOT NULL,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,

    -- Fields that may be unknown
    beds INTEGER,
    baths REAL,
    address TEXT,
    lat REAL,
    lon REAL,
    lease_length TEXT,
    posted_at TEXT,
    image_url TEXT,
    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source, source_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    price INTEGER NOT NULL,
    seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,
    listings_found INTEGER NOT NULL,
    status TEXT NOT NULL
);

-- I made this trigger to update the last_seen field in the listings table whenever a new price_history entry is added. This ensures that the listings table always reflects the most recent time a listing was seen. 
-- dont forget not to add this again in db.py
CREATE TRIGGER IF NOT EXISTS update_seen_at
AFTER INSERT ON price_history
FOR EACH ROW
BEGIN
    UPDATE listings
    SET last_seen = NEW.seen_at
    WHERE id = NEW.listing_id;  
END;