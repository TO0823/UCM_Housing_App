from scraper.db import upsert_listing, add_price


def run_scraper(conn, scraper):
    """Save a complete scrape, or roll back its changes on failure."""

    # Fetch before starting database writes.
    try:
        listings = scraper.scrape()

        for listing in listings:
            listing_id = upsert_listing(conn, listing)
            add_price(conn, listing_id, listing.price)

        conn.execute(
            """
            INSERT INTO runs (source, listings_found, status)
            VALUES (?, ?, ?)
            """,
            (scraper.source, len(listings), "success")
        )

        # Save the entire run together.
        conn.commit()
        return len(listings)

    except Exception:
        # Undo any incomplete listing and price changes.
        conn.rollback()

        # Record the failure in a separate transaction.
        conn.execute(
            """
            INSERT INTO runs (source, listings_found, status)
            VALUES (?, ?, ?)
            """,
            (scraper.source, 0, "failed")
        )

        conn.commit()
        raise