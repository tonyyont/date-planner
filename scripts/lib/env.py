"""Environment and API key management for date-planner."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".config" / "datekit"
CONFIG_FILE = CONFIG_DIR / ".env"


def load_env_file(path: Path) -> Dict[str, str]:
    """Load environment variables from a file."""
    env = {}
    if not path.exists():
        return env

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                if key and value:
                    env[key] = value
    return env


def get_config() -> Dict[str, Any]:
    """Load configuration from ~/.config/datekit/.env and environment."""
    file_env = load_env_file(CONFIG_FILE)

    # Environment variables override file
    config = {
        'TICKETMASTER_API_KEY': os.environ.get('TICKETMASTER_API_KEY') or file_env.get('TICKETMASTER_API_KEY'),
        'GOOGLE_PLACES_API_KEY': os.environ.get('GOOGLE_PLACES_API_KEY') or file_env.get('GOOGLE_PLACES_API_KEY'),
    }

    return config


def get_city() -> Optional[str]:
    """Read city from data/preferences.json."""
    prefs_path = Path(__file__).parent.parent.parent / "data" / "preferences.json"
    if not prefs_path.exists():
        return None
    try:
        with open(prefs_path) as f:
            prefs = json.load(f)
        return prefs.get("city") or None
    except (json.JSONDecodeError, OSError):
        return None


def config_exists() -> bool:
    """Check if configuration file exists."""
    return CONFIG_FILE.exists()


def get_available_sources(config: Dict[str, Any]) -> list:
    """Return list of available data sources based on API keys."""
    sources = ['websearch']  # Always available via Claude
    if config.get('TICKETMASTER_API_KEY'):
        sources.append('ticketmaster')
    if config.get('GOOGLE_PLACES_API_KEY'):
        sources.append('google_places')
    return sources
