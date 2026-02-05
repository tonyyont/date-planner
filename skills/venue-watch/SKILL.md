---
name: venue-watch
description: Monitor your favorite venues and artists for upcoming events
---

# Venue Watch Skill

Monitor your favorite venues and artists for upcoming events.

## Usage

- `/venue-watch` - Check all watched venues for upcoming events
- `/venue-watch add [name]` - Add a venue to watchlist
- `/venue-watch add-artist [name]` - Add an artist to watchlist
- `/venue-watch remove [slug]` - Remove venue from watchlist
- `/venue-watch remove-artist [name]` - Remove artist from watchlist
- `/venue-watch list` - Show current watchlist

## Data Files

- **Watchlist**: `data/watchlist.json` — venues and artists being monitored
- **Venue DB**: `data/venues.json` — full venue database with metadata

## Workflow

### Step 0: Setup Check

Read `data/preferences.json`. If `metadata.setup_complete` is false, say:
> "Run `/date-plan setup` first to set your city and preferences!"

### `/venue-watch` — Check for Events

1. Read `data/watchlist.json` for watched venues and artists
2. Read `data/venues.json` for venue metadata
3. Read city from `data/preferences.json`

4. **For each watched venue with a ticketmaster_venue_id** (if Ticketmaster API available):
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_events.py --venue <slug> --days 30 --format json
   ```

5. **For watched venues WITHOUT Ticketmaster ID:**
   WebSearch: "[venue name] [city] upcoming shows schedule"

6. **For watched artists:**
   - WebSearch: "[artist name] concert [city] 2026"
   - If Ticketmaster available: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_events.py --city "{city}" --artist "<name>" --format json`

7. Display results grouped by venue:

```
## Venue Watch Report
*Last checked: [date]*

### [Venue Name] (category)
1. **[Event]** — [Date] — $XX-XX — [Tickets](url)
2. **[Event]** — [Date] — $XX-XX — [Tickets](url)

### [Venue Name] (category)
No upcoming events found. Check website: [url]

---

### Artist Alerts
No watched artists currently. Add with `/venue-watch add-artist [name]`
```

### `/venue-watch add [name]` — Add a Venue

This is the key flow that builds the venue database organically:

1. Read `data/venues.json` — check if venue already exists (match on name)
2. If not found, **discover the venue via WebSearch**:
   - WebSearch: "[name] [city] venue"
   - Extract: name, address, neighborhood, category, website
3. Create a venue entry:
   ```json
   {
     "slug": "name-slugified",
     "name": "Full Venue Name",
     "category": "music|comedy|theater|museum|food",
     "subcategory": "",
     "neighborhood": "Neighborhood",
     "address": "Address",
     "website": "URL",
     "ticketing_platform": "ticketmaster|axs|direct",
     "ticketmaster_venue_id": null,
     "notes": ""
   }
   ```
4. Add to `data/venues.json`
5. Add slug to `data/watchlist.json` `watched_venues`
6. If Ticketmaster API available, search for venue ID:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_venues.py --venue "[name]"
   ```
   Update the entry if found.
7. Confirm: "Added **[Venue Name]** to your watchlist! ([category], [neighborhood])"
8. Git commit: `git add data/venues.json data/watchlist.json && git commit -m "date-planner: watch [venue-name]"`

### `/venue-watch add-artist [name]`

1. Add to `data/watchlist.json` `watched_artists` array
2. Immediately search:
   - WebSearch: "[artist name] concert [city] 2026 tour dates"
   - If Ticketmaster available: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_events.py --city "{city}" --artist "<name>" --format json`
3. Show results or: "No upcoming dates for [artist] in [city]. I'll flag them when they're announced."
4. Git commit

### `/venue-watch remove [slug]`

1. Remove from `data/watchlist.json` `watched_venues`
2. Confirm and git commit

### `/venue-watch remove-artist [name]`

1. Remove from `data/watchlist.json` `watched_artists`
2. Confirm and git commit

### `/venue-watch list`

Display current watchlist with venue details:

```
## Your Watchlist

### Venues ([count])

**Music:**
- [Venue Name] ([subcategory], [neighborhood])

**Comedy:**
- [Venue Name] ([neighborhood])

**Museums:**
- [Venue Name] ([neighborhood])

### Artists ([count])
- [Artist Name]

---
*[N] venues in database total. Add more with `/venue-watch add [name]`*
```

## Notes

- Ticketmaster API: 5000 calls/day limit. Checking venues = 1 call each.
- Comedy venues often don't have Ticketmaster listings → WebSearch fills the gap
- Museums don't have "events" in Ticketmaster → WebSearch for exhibitions
