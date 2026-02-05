#!/usr/bin/env python3
"""Populate Ticketmaster venue IDs for venues in venues.json.

Usage:
    python3 fetch_venues.py                    # Update all venues missing TM IDs
    python3 fetch_venues.py --check            # Show which venues need TM IDs
    python3 fetch_venues.py --state CA         # Search with state filter
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.env import get_config
from lib.ticketmaster import search_venue_id

REPO_ROOT = Path(__file__).parent.parent
VENUES_FILE = REPO_ROOT / "data" / "venues.json"


def load_venues_data():
    """Load venues data. Returns (venues_list, is_flat_array)."""
    with open(VENUES_FILE) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data, True
    return data.get("venues", []), False


def save_venues_data(venues: list, is_flat_array: bool):
    """Save venues data back to file in the original format."""
    if is_flat_array:
        data = venues
    else:
        data = {"venues": venues}
    with open(VENUES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Populate Ticketmaster venue IDs")
    parser.add_argument("--check", action="store_true",
                        help="Just show which venues need IDs (don't update)")
    parser.add_argument("--city", help="City filter (for consistency, not used in venue search)")
    parser.add_argument("--state", help="State code for Ticketmaster search (e.g., CA, NY)")
    args = parser.parse_args()

    config = get_config()
    api_key = config.get("TICKETMASTER_API_KEY")

    venues, is_flat_array = load_venues_data()

    needs_id = [v for v in venues
                if v.get("ticketing_platform") == "ticketmaster"
                and not v.get("ticketmaster_venue_id")]

    has_id = [v for v in venues
              if v.get("ticketmaster_venue_id")]

    print(f"Venue stats: {len(has_id)} have TM IDs, {len(needs_id)} need TM IDs")
    print(f"Total venues: {len(venues)}")
    print()

    if args.check:
        if needs_id:
            print("Venues needing Ticketmaster IDs:")
            for v in needs_id:
                print(f"  - {v['name']} ({v['slug']})")
        else:
            print("All ticketmaster-platform venues have IDs!")
        return

    if not api_key:
        print("Error: No TICKETMASTER_API_KEY configured.")
        print("Add to ~/.config/datekit/.env:")
        print('  TICKETMASTER_API_KEY=your-key-here')
        print()
        print("Get a free key at: https://developer.ticketmaster.com")
        return

    if not needs_id:
        print("All ticketmaster-platform venues already have IDs.")
        return

    state_code = args.state or ""
    print(f"Searching Ticketmaster for {len(needs_id)} venues...")
    if state_code:
        print(f"  State filter: {state_code}")
    print()

    updated = 0
    for v in needs_id:
        tm_id = search_venue_id(v["name"], state_code=state_code)
        if tm_id:
            v["ticketmaster_venue_id"] = tm_id
            print(f"  Found: {v['name']} -> {tm_id}")
            updated += 1
        else:
            print(f"  Not found: {v['name']}")
        time.sleep(0.25)  # Rate limit: 5 req/sec

    save_venues_data(venues, is_flat_array)

    print(f"\nUpdated {updated} venue(s).")


if __name__ == "__main__":
    main()
