import pytest
from scraper.parse import parse_price, parse_beds, parse_baths


@pytest.mark.parametrize("text, expected", [
    ("$1,350/mo", 1350),
    ("$2,000", 2000),
    ("$950 per month", 950),
    ("$1,200 - $1,500", 1200),
    ("Call for Rent", None),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("Studio", 0),
    ("1 Bed", 1),
    ("2 Beds", 2),
    ("3 Bedrooms", 3),
    ("1-2 Beds", 1),
    ("2-3 Beds", 2),
    ("1 - 3 bd ", 1),
    ("2 bd", 2),
    ("2bd 1ba", 2),
    ("Contact for Details", None),
])
def test_parse_beds(text, expected):
    assert parse_beds(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("1 Bath", 1.0),
    ("1.5 Baths", 1.5),
    ("1 - 2 ba ", 1.0),
    ("2 ba", 2.0),
    ("2bd 1ba", 1.0),
    ("2 1/2 Baths", 2.5),
    ("2 Baths", 2.0),
    ("Call for Details", None),
])

def test_parse_baths(text, expected):
    result = parse_baths(text)

    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected)