"""Ticketmaster Discovery API client for date-planner.

API docs: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
Free tier: 5000 calls/day, 5 calls/second.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http, cache
from .env import get_config

BASE_URL = "https://app.ticketmaster.com/discovery/v2"


def _get_api_key() -> Optional[str]:
    config = get_config()
    return config.get('TICKETMASTER_API_KEY')


def search_events(
    venue_id: Optional[str] = None,
    keyword: Optional[str] = None,
    classification_name: Optional[str] = None,  # "Music", "Comedy", "Theatre"
    start_date: Optional[str] = None,  # YYYY-MM-DD
    end_date: Optional[str] = None,  # YYYY-MM-DD
    city: str = "",
    state_code: str = "",
    size: int = 20,
    sort: str = "date,asc",
) -> Dict[str, Any]:
    """Search Ticketmaster events.

    Returns dict with 'events' list and 'total' count.
    """
    api_key = _get_api_key()
    if not api_key:
        return {"error": "No TICKETMASTER_API_KEY configured. Add to ~/.config/datekit/.env", "events": []}

    # Build cache key
    cache_key = cache.get_cache_key(
        f"tm-{venue_id}-{keyword}-{classification_name}-{city}",
        start_date or "",
        end_date or "",
        "ticketmaster"
    )
    cached = cache.load_cache(cache_key, ttl_hours=6)
    if cached:
        return cached

    params = {
        "apikey": api_key,
        "size": size,
        "sort": sort,
    }

    if city:
        params["city"] = city
    if state_code:
        params["stateCode"] = state_code
    if venue_id:
        params["venueId"] = venue_id
    if keyword:
        params["keyword"] = keyword
    if classification_name:
        params["classificationName"] = classification_name
    if start_date:
        params["startDateTime"] = f"{start_date}T00:00:00Z"
    if end_date:
        params["endDateTime"] = f"{end_date}T23:59:59Z"

    url = f"{BASE_URL}/events.json?{urlencode(params)}"

    try:
        data = http.get(url)
        events = _parse_events(data)
        result = {"events": events, "total": data.get("page", {}).get("totalElements", 0)}
        cache.save_cache(cache_key, result)
        return result
    except http.HTTPError as e:
        return {"error": str(e), "events": []}


def get_venue_events(venue_id: str, days_ahead: int = 30) -> Dict[str, Any]:
    """Get upcoming events at a specific venue."""
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    return search_events(venue_id=venue_id, start_date=start, end_date=end)


def search_artist(artist_name: str, city: str = "", state_code: str = "") -> Dict[str, Any]:
    """Search for an artist and their upcoming events."""
    api_key = _get_api_key()
    if not api_key:
        return {"error": "No TICKETMASTER_API_KEY configured", "events": []}

    cache_key = cache.get_cache_key(
        f"tm-artist-{artist_name}-{city}",
        "", "",
        "ticketmaster"
    )
    cached = cache.load_cache(cache_key, ttl_hours=6)
    if cached:
        return cached

    params = {
        "apikey": api_key,
        "keyword": artist_name,
        "size": 10,
        "sort": "date,asc",
    }

    if city:
        params["city"] = city
    if state_code:
        params["stateCode"] = state_code

    url = f"{BASE_URL}/events.json?{urlencode(params)}"

    try:
        data = http.get(url)
        result = {"events": _parse_events(data)}
        cache.save_cache(cache_key, result)
        return result
    except http.HTTPError as e:
        return {"error": str(e), "events": []}


def search_venue_id(venue_name: str, state_code: str = "") -> Optional[str]:
    """Search Ticketmaster for a venue and return its ID."""
    api_key = _get_api_key()
    if not api_key:
        return None

    params = {
        "apikey": api_key,
        "keyword": venue_name,
        "size": 5,
    }

    if state_code:
        params["stateCode"] = state_code

    url = f"{BASE_URL}/venues.json?{urlencode(params)}"

    try:
        data = http.get(url)
        venues = data.get("_embedded", {}).get("venues", [])
        for v in venues:
            if venue_name.lower() in v.get("name", "").lower():
                return v["id"]
        return venues[0]["id"] if venues else None
    except Exception:
        return None


def _parse_events(data: Dict) -> List[Dict]:
    """Parse Ticketmaster API response into clean event dicts."""
    events = []
    embedded = data.get("_embedded", {})
    for ev in embedded.get("events", []):
        event = {
            "name": ev.get("name"),
            "date": ev.get("dates", {}).get("start", {}).get("localDate"),
            "time": ev.get("dates", {}).get("start", {}).get("localTime"),
            "venue": _extract_venue(ev),
            "price_range": _extract_price(ev),
            "url": ev.get("url"),
            "genre": _extract_genre(ev),
            "image": _extract_image(ev),
        }
        events.append(event)
    return events


def _extract_venue(ev: Dict) -> Dict:
    """Extract venue info from event."""
    venues = ev.get("_embedded", {}).get("venues", [])
    if venues:
        v = venues[0]
        return {"name": v.get("name"), "id": v.get("id")}
    return {}


def _extract_price(ev: Dict) -> Optional[Dict]:
    """Extract price range from event."""
    ranges = ev.get("priceRanges", [])
    if ranges:
        r = ranges[0]
        return {"min": r.get("min"), "max": r.get("max"), "currency": r.get("currency", "USD")}
    return None


def _extract_genre(ev: Dict) -> Optional[str]:
    """Extract genre from event classifications."""
    classifications = ev.get("classifications", [])
    if classifications:
        return classifications[0].get("genre", {}).get("name")
    return None


def _extract_image(ev: Dict) -> Optional[str]:
    """Extract best image URL from event."""
    images = ev.get("images", [])
    for img in images:
        if img.get("ratio") == "16_9" and img.get("width", 0) >= 500:
            return img.get("url")
    return images[0].get("url") if images else None
