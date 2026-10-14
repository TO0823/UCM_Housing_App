"""Tests: distance between two known Merced points matches Google Maps within ~0.1 mi."""

import pytest
from scraper.geo import UCM_LAT, UCM_LON, miles_between


def test_same_location():
    distance = miles_between(37.366, -120.424, 37.366, -120.424)

    assert distance == pytest.approx(0)


def test_one_degree_latitude():
    distance = miles_between(0, 0, 1, 0)

    assert distance == pytest.approx(69.1, abs=0.1)

def test_campus_to_target_straight_line():
    target_lat = 37.32299071338703
    target_lon = -120.4849359166065
    expected_miles = 3.97

    distance = miles_between(
        UCM_LAT,
        UCM_LON,
        target_lat,
        target_lon
    )

    assert distance == pytest.approx(expected_miles, abs=0.1)
