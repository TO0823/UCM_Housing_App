import re

def parse_price(text: str) -> int | None:
    # Convert a rental price into an integer.
    match = re.search(r"\$\s*([\d,]+)", text)

    if match is None:
        return None

    price_str = match.group(1).replace(",", "")
    return int(price_str)
# ---------------------------------------------------------------------------------------
def parse_beds(text: str) -> int | None:
    """Return bedroom count, using the minimum for ranges."""

    if "studio" in text.lower():
        return 0

    match = re.search(
        r"(\d+)\s*(?:-\s*(\d+)\s*)?(?:Bedrooms?|Beds?|bd\b)",
        text,
        re.IGNORECASE
    )

    if match is None:
        return None

    return int(match.group(1))
# ---------------------------------------------------------------------------------------
def parse_baths(text: str) -> float | None:
    # Handle mixed fractions like "2 1/2 Baths"
    fraction = re.search(
        r"(\d+)\s+(\d+)/(\d+)\s*(?:Baths?|Bathrooms?)",
        text,
        re.IGNORECASE
    )

    if fraction:
        whole = int(fraction.group(1))
        numerator = int(fraction.group(2))
        denominator = int(fraction.group(3))

        if denominator == 0:
            return None

        return whole + numerator / denominator

    # Handle normal numbers like "1 Bath" or "1.5 Baths"
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:-\s*\d+(?:\.\d+)?\s*)?(?:Bathrooms?|Baths?|ba\b)",
        text,
        re.IGNORECASE
    )

    if match is None:
        return None

    return float(match.group(1))