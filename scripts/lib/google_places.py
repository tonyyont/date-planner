"""Google Places API client for date-planner restaurant discovery.

Uses the Places API (New) v1.
Free $200/month credit covers typical usage.
"""

import json
from typing import Any, Dict, List, Optional

from . import http, cache
from .env import get_config

SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"


def _get_api_key() -> Optional[str]:
    config = get_config()
    return config.get('GOOGLE_PLACES_API_KEY')


def search_restaurants(
    query: str,
    city: str = "",
    neighborhood: Optional[str] = None,
    open_now: bool = False,
    max_results: int = 10,
) -> Dict[str, Any]:
    """Search for restaurants in a city.

    Args:
        query: Search query (e.g., "Thai restaurant", "romantic dinner")
        city: City to search in (e.g., "Los Angeles", "New York")
        neighborhood: Optional neighborhood to focus on
        open_now: Only return currently open places
        max_results: Max results to return (default 10)

    Returns:
        Dict with 'places' list or 'error' string
    """
    api_key = _get_api_key()
    if not api_key:
        return {"error": "No GOOGLE_PLACES_API_KEY configured. Add to ~/.config/datekit/.env", "places": []}

    # Cache key
    cache_key = cache.get_cache_key(
        f"gp-{query}-{city}-{neighborhood}",
        "", "",
        "google_places"
    )
    cached = cache.load_cache(cache_key, ttl_hours=24)
    if cached:
        return cached

    if city:
        search_query = f"{query} restaurant {city}"
    else:
        search_query = f"{query} restaurant"
    if neighborhood:
        search_query += f" {neighborhood}"

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel,places.rating,places.userRatingCount,places.websiteUri,places.googleMapsUri,places.regularOpeningHours",
        "Content-Type": "application/json",
    }

    body = {
        "textQuery": search_query,
        "maxResultCount": max_results,
    }

    if open_now:
        body["openNow"] = True

    try:
        data = http.post(SEARCH_TEXT_URL, json_data=body, headers=headers)
        places = _parse_places(data)
        result = {"places": places}
        cache.save_cache(cache_key, result)
        return result
    except http.HTTPError as e:
        return {"error": str(e), "places": []}


def _parse_places(data: Dict) -> List[Dict]:
    """Parse Google Places response into clean dicts."""
    places = []
    for p in data.get("places", []):
        place = {
            "name": p.get("displayName", {}).get("text"),
            "address": p.get("formattedAddress"),
            "price_level": p.get("priceLevel"),
            "rating": p.get("rating"),
            "review_count": p.get("userRatingCount"),
            "website": p.get("websiteUri"),
            "maps_url": p.get("googleMapsUri"),
        }
        places.append(place)
    return places
