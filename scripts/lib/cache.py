"""Caching utilities for date-planner."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path.home() / ".cache" / "datekit"
DEFAULT_TTL_HOURS = 6  # Events change frequently


def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(topic: str, from_date: str, to_date: str, sources: str) -> str:
    """Generate a cache key from query parameters."""
    key_data = f"{topic}|{from_date}|{to_date}|{sources}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cache_path(cache_key: str) -> Path:
    """Get path to cache file."""
    return CACHE_DIR / f"{cache_key}.json"


def is_cache_valid(cache_path: Path, ttl_hours: int = DEFAULT_TTL_HOURS) -> bool:
    """Check if cache file exists and is within TTL."""
    if not cache_path.exists():
        return False

    try:
        stat = cache_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = (now - mtime).total_seconds() / 3600
        return age_hours < ttl_hours
    except OSError:
        return False


def load_cache(cache_key: str, ttl_hours: int = DEFAULT_TTL_HOURS) -> Optional[dict]:
    """Load data from cache if valid."""
    cache_path = get_cache_path(cache_key)

    if not is_cache_valid(cache_path, ttl_hours):
        return None

    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(cache_key: str, data: dict):
    """Save data to cache."""
    ensure_cache_dir()
    cache_path = get_cache_path(cache_key)

    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    except OSError:
        pass  # Silently fail on cache write errors


def clear_cache():
    """Clear all cache files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
            except OSError:
                pass
