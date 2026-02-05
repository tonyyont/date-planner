# date-planner

A Claude Code skill for planning dates. Works in any city. Finds real events, restaurants, and activities personalized to your relationship(s).

## Skills

### `/date-plan` — Main Date Planner
Plan dates with concrete venue + food + timing options.
- `/date-plan` — Interactive planning
- `/date-plan this weekend` — Quick plan for this weekend
- `/date-plan adventure` — Category-focused planning
- `/date-plan rate` — Rate your last date
- `/date-plan history` — View date history and category balance
- `/date-plan setup` — First-time setup or update preferences

### `/events` — Event Finder
Find what's happening in your city.
- `/events` — This week, all categories
- `/events music` — Concerts only
- `/events comedy this weekend` — Comedy this weekend
- `/events theater` — Theater/broadway
- `/events food` — Food events and pop-ups
- `/events museums` — Current exhibitions

### `/venue-watch` — Venue Monitoring
Track favorite venues and artists for upcoming events.
- `/venue-watch` — Check all watched venues
- `/venue-watch add [name]` — Add venue to watchlist
- `/venue-watch add-artist [name]` — Watch an artist
- `/venue-watch list` — Show current watchlist

### `/find-class` — Class/Experience Finder
Find classes and activities.
- `/find-class martial-arts` — BJJ, taekwondo, kickboxing
- `/find-class cooking` — Cooking classes
- `/find-class pottery` — Pottery/ceramics
- `/find-class art` — Paint & sip, stained glass
- `/find-class [query]` — Custom search

## Data Architecture

| File | Purpose |
|------|---------|
| `data/preferences.json` | User info, partners, city, food prefs, date style |
| `data/venues.json` | Venue database (grows as you use it) |
| `data/date-history.json` | Log of past dates with ratings |
| `data/watchlist.json` | Venues and artists being monitored |

## First-Time Setup

Run `/date-plan` — it will walk you through setup:
1. Your name and partner(s)
2. City
3. Food preferences, date style, budget
4. Bucket list items
5. Auto-discovers popular venues in your city

## Optional: API Keys (Better Results)

date-planner works out of the box with web search. For richer results:

```bash
mkdir -p ~/.config/datekit
echo 'TICKETMASTER_API_KEY=your-key-here' > ~/.config/datekit/.env
echo 'GOOGLE_PLACES_API_KEY=your-key-here' >> ~/.config/datekit/.env
```

- **Ticketmaster** (free): https://developer.ticketmaster.com — better music/theater event data
- **Google Places** (free $200/mo): better restaurant discovery with ratings

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fetch_events.py` | Fetch events from Ticketmaster API |
| `scripts/fetch_venues.py` | Populate Ticketmaster venue IDs |
| `scripts/fetch_classes.py` | Generate class search queries |
| `scripts/lib/` | Shared library (env, http, cache, API clients) |

## Conventions

- **Config**: `~/.config/datekit/.env` (never committed)
- **Cache**: `~/.cache/datekit/` (JSON files, 6hr TTL for events)
- **Data**: JSON files in `data/`, git-versioned
- **Python**: stdlib only (no pip dependencies)

## Date Categories

| Category | Energy | Examples |
|----------|--------|----------|
| Adventure | High | Hiking, concerts, martial arts, sports |
| Creative | Medium | Pottery, cooking class, stained glass |
| Explore | Medium | Estate sales, neighborhoods, museums, markets |
| Nourish | Low-Med | Restaurant discovery, food tours, cooking together |
| Recharge | Low | Spa, beach, movie night, scenic drives |
