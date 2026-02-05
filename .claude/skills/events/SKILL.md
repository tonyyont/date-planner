---
name: events
description: Find what's happening in your city — concerts, comedy, theater, food events, museum exhibitions
---

# Events Skill

Find real upcoming events in your city across music, comedy, theater, food, and museums.

## Usage

- `/events` - What's happening this week (all categories)
- `/events music` - Music/concerts only
- `/events comedy` - Comedy shows
- `/events comedy this weekend` - Comedy this weekend
- `/events theater` - Theater/broadway shows
- `/events food` - Food events and pop-ups
- `/events museums` - Current museum exhibitions
- `/events all next week` - Everything next week

## Workflow

### Step 0: Setup Check

Read `data/preferences.json`. If `metadata.setup_complete` is false, say:
> "Run `/date-plan setup` first to set your city and preferences!"

### Step 1: Parse Input

Read city from `data/preferences.json`.

Extract from arguments:
- **Category**: music, comedy, theater, food, museums, all (default: all)
- **Timeframe**: "tonight", "this weekend", "this week", "next week", "next 2 weeks" (default: this week)

Convert timeframe to concrete dates:
- "tonight" → today only
- "this weekend" → upcoming Saturday + Sunday
- "this week" → today through Sunday
- "next week" → next Monday through Sunday
- "next 2 weeks" → today + 14 days

### Step 2: Fetch Events by Category

**Music:**
- WebSearch: "concerts {city} this week", "live music {city} this weekend"
- If Ticketmaster API available: `python3 scripts/fetch_events.py --city "{city}" --category music --days {N} --format json`

**Theater:**
- WebSearch: "theater shows {city} now playing", "broadway {city} current"
- If Ticketmaster API available: `python3 scripts/fetch_events.py --city "{city}" --category theatre --days {N} --format json`

**Comedy:**
- WebSearch: "comedy shows {city} this week", "stand up comedy {city} this weekend"
- Check `data/venues.json` for comedy venues, search each by name: "[venue name] upcoming shows"

**Food Events:**
- WebSearch: "food events {city} this week", "food festival {city} this month", "pop up restaurant {city}"

**Museums:**
- WebSearch: "museum exhibitions {city} now", "art exhibitions {city} current"
- Check `data/venues.json` for museums, search each by name: "[museum name] current exhibitions"

### Step 3: Format and Display Results

Group by category, sorted by date within each:

```
## Music

1. **[Artist/Show Name]** — [Venue Name]
   [Day, Date] at [Time] | $XX-XX | [Tickets](url)

2. **[Artist/Show Name]** — [Venue Name]
   [Day, Date] at [Time] | $XX-XX | [Tickets](url)

## Comedy

1. **[Show/Comedian]** — [Venue]
   [Day, Date] at [Time] | $XX | [Info](url)

## Theater

1. **[Show Name]** — [Venue]
   Now through [end date] | $XX-XX | [Tickets](url)

## Food Events

1. **[Event Name]** — [Location]
   [Dates] | [Details]

## Museum Exhibitions

1. **[Exhibition Name]** — [Museum]
   Through [end date] | [Price/Free] | [Details]
```

If a category has no results:
> No [category] events found for this period.

### Step 4: Offer Next Steps

> **What next?**
> - Turn something into a date plan → `/date-plan`
> - Add a venue to your watchlist → `/venue-watch add [name]`
> - Search for a specific artist → just ask!

## Special Handling

### Artist Search
If user asks about a specific artist (e.g., `/events "Radiohead"`):
- WebSearch: "[artist name] concert {city} 2026"
- If Ticketmaster available: `python3 scripts/fetch_events.py --city "{city}" --artist "name" --format json`

### Venue-Specific
If user asks about a specific venue (e.g., `/events metro`):
- Find venue in `data/venues.json`
- If found with Ticketmaster ID: `python3 scripts/fetch_events.py --venue {slug} --days 30 --format json`
- If no Ticketmaster ID: WebSearch "[venue name] upcoming shows schedule"

## Error Handling

- **No API keys**: Use WebSearch for all categories. Note: "Set up a Ticketmaster API key for better music/theater results. See README.md for setup."
- **Not set up yet**: Direct to `/date-plan setup`
- **No events found**: Suggest checking venue websites, WebSearch broader queries
