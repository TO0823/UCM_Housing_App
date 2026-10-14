
"""Calculate driving distance and time to UC Merced using Google Routes API."""

import os
import requests
from dotenv import load_dotenv
from scraper.geo import UCM_LAT, UCM_LON

load_dotenv()

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def driving_route(origin_address: str) -> tuple[float, float]:
    """Return (driving miles, driving minutes) to UC Merced."""

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is missing from .env")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration",
    }

    body = {
        "origin": {
            "address": origin_address
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": UCM_LAT,
                    "longitude": UCM_LON
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_UNAWARE",
    }

    response = requests.post(
        ROUTES_URL,
        headers=headers,
        json=body,
        timeout=20
    )

    response.raise_for_status()

    routes = response.json().get("routes", [])

    if not routes:
        raise ValueError("Google Maps returned no driving route")

    route = routes[0]

    miles = route["distanceMeters"] / 1609.344
    minutes = float(route["duration"].removesuffix("s")) / 60

    return miles, minutes
