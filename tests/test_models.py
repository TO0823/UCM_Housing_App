"""Tests for valid listings and missing required fields."""

import pytest
from scraper.models import Listing


def test_major_listing_fields():
    # Providing all required fields should create a listing.
    listing = Listing(
        price=1000,
        url="http://example.com",
        source="example",
        source_id="123",
    )

    assert listing.price == 1000
    assert listing.url == "http://example.com"
    assert listing.source == "example"
    assert listing.source_id == "123"


def test_missing_listing_fields():
    # Omitting the required price should raise TypeError.
    with pytest.raises(TypeError):
        Listing(
            url="http://example.com",
            source="example",
            source_id="123",
        )