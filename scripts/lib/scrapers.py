"""Query builders for event/class data.

These functions generate search queries for Claude's WebSearch tool.
Actual web searching is done by Claude, not by these scripts.
"""

from datetime import datetime
from typing import List


def comedy_search_queries(city: str, date_range: str = "") -> List[str]:
    """Generate search queries for comedy shows in a city."""
    today = datetime.now().strftime("%Y-%m-%d")
    month_year = datetime.now().strftime("%B %Y")
    return [
        f"comedy shows {city} this week {today}",
        f"stand up comedy {city} this weekend",
        f"best comedy clubs {city} upcoming shows {month_year}",
        f"comedy events {city} tonight",
    ]


def theater_search_queries(city: str) -> List[str]:
    """Generate search queries for theater in a city."""
    return [
        f"theater shows {city} now playing",
        f"broadway shows {city} current",
        f"live theater {city} this month",
        f"performing arts {city} upcoming shows",
    ]


def food_event_search_queries(city: str) -> List[str]:
    """Generate search queries for food events in a city."""
    month_year = datetime.now().strftime("%B %Y")
    return [
        f"food events {city} {month_year}",
        f"food festival {city} this month",
        f"pop up restaurant {city} this week",
        f"restaurant week {city} 2026",
    ]


def museum_exhibition_queries(city: str) -> List[str]:
    """Generate search queries for museum exhibitions in a city."""
    month_year = datetime.now().strftime("%B %Y")
    return [
        f"museum exhibitions {city} {month_year}",
        f"art exhibitions {city} now",
        f"best museums {city} current shows",
        f"free museum days {city} this month",
    ]


def class_search_queries(category: str, city: str) -> List[str]:
    """Generate search queries for classes/experiences in a city."""
    queries = {
        "martial-arts": [
            f"BJJ beginner class {city} free trial",
            f"martial arts intro class {city}",
            f"kickboxing beginner class {city}",
            f"martial arts couples class {city}",
        ],
        "cooking": [
            f"cooking class {city} couples",
            f"cooking class {city} date night",
            f"best cooking classes {city}",
            f"pasta making class {city}",
        ],
        "pottery": [
            f"pottery class {city} beginners drop-in",
            f"ceramic class {city} couples",
            f"wheel throwing class {city} beginner",
        ],
        "art": [
            f"paint and sip {city}",
            f"art class {city} beginners",
            f"stained glass class {city}",
            f"drawing class {city} drop-in",
        ],
        "general": [
            f"couples activities {city}",
            f"unique date experiences {city}",
            f"ClassBento {city}",
            f"Airbnb experiences {city}",
        ],
    }
    return queries.get(category, queries["general"])
