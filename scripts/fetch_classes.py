#!/usr/bin/env python3
"""Generate search queries for classes and experiences.

Outputs search queries that Claude's WebSearch tool can execute,
plus platform suggestions for manual browsing.

Usage:
    python3 fetch_classes.py --category martial-arts
    python3 fetch_classes.py --category cooking --city "New York"
    python3 fetch_classes.py --query "pottery class couples"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.env import get_city
from lib.scrapers import class_search_queries


PLATFORMS = [
    {"name": "ClassBento", "url": "https://classbento.com", "focus": "Creative classes"},
    {"name": "Coursehorse", "url": "https://coursehorse.com", "focus": "All class types"},
    {"name": "Airbnb Experiences", "url": "https://www.airbnb.com/s/experiences", "focus": "Unique local experiences"},
    {"name": "Groupon", "url": "https://www.groupon.com/local/things-to-do", "focus": "Deals on classes"},
]


def main():
    parser = argparse.ArgumentParser(description="Find classes and experiences")
    parser.add_argument("--category", choices=[
        "martial-arts", "cooking", "pottery", "art", "general"
    ], help="Class category")
    parser.add_argument("--query", help="Custom search query")
    parser.add_argument("--city", help="City to search in (default: from preferences.json)")
    parser.add_argument("--format", choices=["json", "compact"], default="json",
                        help="Output format")

    args = parser.parse_args()

    # Resolve city: CLI arg > preferences.json
    city = args.city or get_city() or ""

    if not city:
        print("Warning: No city specified. Use --city or set city in data/preferences.json", file=sys.stderr)

    if args.query:
        if city:
            queries = [f"{args.query} {city}"]
        else:
            queries = [args.query]
        category = "custom"
    elif args.category:
        queries = class_search_queries(args.category, city)
        category = args.category
    else:
        parser.print_help()
        print("\n\nAvailable categories:")
        print("  martial-arts  BJJ, taekwondo, kickboxing intro classes")
        print("  cooking       Thai, Italian, sushi, pasta making")
        print("  pottery       Ceramics, wheel throwing")
        print("  art           Paint & sip, stained glass, drawing")
        print("  general       Browse all class types")
        return

    output = {
        "category": category,
        "city": city,
        "search_queries": queries,
        "platforms": PLATFORMS,
    }

    if args.format == "json":
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output, separators=(',', ':')))


if __name__ == "__main__":
    main()
