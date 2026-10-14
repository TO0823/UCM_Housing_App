"""Listing dataclass: the one shape every source scraper must return
(price, beds, baths, address, lat/lon, lease_length, posted_at, url, image_url, source, source_id)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Listing:
    # Required:
    price: int
    url: str
    source: str
    source_id: str

    # May be unknown:
    beds: Optional[int] = None
    baths: Optional[float] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    lease_length: Optional[str] = None
    posted_at: Optional[datetime] = None
    image_url: Optional[str] = None