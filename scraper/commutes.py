
"""Calculate driving commutes for unique property addresses."""

from scraper.routes import driving_route


def get_commutes(addresses: list[str]) -> dict[str, tuple[float, float]]:
    """Return driving miles and minutes for unique addresses."""

    results = {}

    for address in addresses:
        if not address or not address.strip():
            continue

        address = address.strip()

        if address in results:
            continue

        miles, minutes = driving_route(address)
        results[address] = (miles, minutes)

    return results

def get_addresses_from_db(conn) -> list[str]:
    """Get unique apartment addresses from SQLite."""

    rows = conn.execute(
        """
        SELECT DISTINCT address
        FROM listings
        WHERE address IS NOT NULL
          AND TRIM(address) != ''
        """
    ).fetchall()

    return [row[0] for row in rows]