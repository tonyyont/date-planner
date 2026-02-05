#!/usr/bin/env python3
"""Fetch upcoming events from Ticketmaster.

Usage:
    python3 fetch_events.py --category music --days 14
    python3 fetch_events.py --category comedy --days 7 --city "New York"
    python3 fetch_events.py --venue hollywood-bowl
    python3 fetch_events.py --artist "Radiohead" --city "Los Angeles"
    python3 fetch_events.py --all --days 7
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.env import get_city
from lib.ticketmaster import search_events, get_venue_events, search_artist

REPO_ROOT = Path(__file__).parent.parent
VENUES_FILE = REPO_ROOT / "data" / "venues.json"


def load_venues() -> list:
    """Load venue database. Handles flat array format."""
    with open(VENUES_FILE) as f:
        data = json.load(f)
    # Handle both flat array and {"venues": [...]} formats
    if isinstance(data, list):
        return data
    return data.get("venues", [])


def fetch_by_category(category: str, days: int = 14, city: str = "", state_code: str = "") -> dict:
    """Fetch events for a category (music, comedy, theatre)."""
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    classification_map = {
        "music": "Music",
        "comedy": "Comedy",
        "theatre": "Theatre",
        "theater": "Theatre",
    }

    classification = classification_map.get(category.lower())
    if not classification:
        return {"error": f"Unknown category: {category}. Use: music, comedy, theatre", "events": []}

    return search_events(
        classification_name=classification,
        start_date=start,
        end_date=end,
        city=city,
        state_code=state_code,
        size=20,
    )


def fetch_by_venue(venue_slug: str, days: int = 30) -> dict:
    """Fetch events for a specific venue by slug."""
    venues = load_venues()
    venue = None
    for v in venues:
        if v["slug"] == venue_slug:
            venue = v
            break

    if not venue:
        # Try partial match
        for v in venues:
            if venue_slug.lower() in v["slug"] or venue_slug.lower() in v["name"].lower():
                venue = v
                break

    if not venue:
        return {"error": f"Venue not found: {venue_slug}. Use a slug from venues.json"}

    tm_id = venue.get("ticketmaster_venue_id")
    if not tm_id:
        return {
            "venue": venue["name"],
            "note": f"No Ticketmaster ID for {venue['name']}. Check website: {venue.get('website', 'N/A')}",
            "events": []
        }

    result = get_venue_events(tm_id, days)
    result["venue"] = venue["name"]
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch events from Ticketmaster")
    parser.add_argument("--category", choices=["music", "comedy", "theatre", "theater"],
                        help="Event category to search")
    parser.add_argument("--venue", help="Venue slug from venues.json")
    parser.add_argument("--artist", help="Search for artist events")
    parser.add_argument("--all", action="store_true", help="Fetch all categories")
    parser.add_argument("--days", type=int, default=14, help="Days ahead to search (default: 14)")
    parser.add_argument("--city", help="City to search in (default: from preferences.json)")
    parser.add_argument("--state", help="State code (e.g., CA, NY)")
    parser.add_argument("--format", choices=["json", "compact"], default="compact",
                        help="Output format (default: compact)")

    args = parser.parse_args()

    # Resolve city: CLI arg > preferences.json
    city = args.city or get_city() or ""
    state_code = args.state or ""

    if not city and not args.venue:
        print("Warning: No city specified. Use --city or set city in data/preferences.json", file=sys.stderr)

    if args.artist:
        result = search_artist(args.artist, city=city, state_code=state_code)
    elif args.venue:
        result = fetch_by_venue(args.venue, args.days)
    elif args.category:
        result = fetch_by_category(args.category, args.days, city=city, state_code=state_code)
    elif args.all:
        result = {
            "music": fetch_by_category("music", args.days, city=city, state_code=state_code),
            "comedy": fetch_by_category("comedy", args.days, city=city, state_code=state_code),
            "theatre": fetch_by_category("theatre", args.days, city=city, state_code=state_code),
        }
    else:
        parser.print_help()
        return

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, separators=(',', ':')))


if __name__ == "__main__":
    main()
