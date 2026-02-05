---
name: date-plan
description: Plan a date — find real events, restaurants, and activities personalized to your relationship
---

# Date Plan Skill

Generate concrete, personalized date plans with real venues, food pairings, and timing.

## Usage

- `/date-plan` - Interactive planning (asks questions)
- `/date-plan this weekend` - Plans for this weekend
- `/date-plan tonight low-energy` - Quick low-energy options
- `/date-plan adventure` - Adventure category focus
- `/date-plan rate` - Rate your last date
- `/date-plan history` - View date history and category balance
- `/date-plan setup` - First-time setup or update preferences

## Workflow

### Step 0: Setup Check

Read `data/preferences.json`. If `metadata.setup_complete` is false:

1. Say: "Welcome to date-planner! Let's get you set up (~2 min)."
2. Run the **First-Time Onboarding** flow (see below)
3. After setup completes, continue to the requested command

### Step 1: Gather Context

Read these files for personalization:

1. `data/preferences.json` - user info, partners, city, shared preferences, things to try
2. `data/date-history.json` - recent dates and category balance
3. `data/venues.json` - known venues in their city

Determine which partner this date is for:
- If 1 partner: use them automatically
- If 2+ partners: ask "Who are you planning for?" and list partner names

### Step 2: Parse Input or Ask

If user provided arguments, parse:
- **Timeframe**: "tonight", "tomorrow", "this weekend", "next week", specific date
- **Energy level**: "low", "medium", "high" (default from preferences)
- **Category**: "adventure", "creative", "explore", "nourish", "recharge"
- **Budget**: "free", "budget" (<$30), "moderate" ($30-80), "splurge" ($80+)

If no arguments or just `/date-plan`, ask:

> **Let's plan a date!**
>
> 1. **When?** (tonight / tomorrow / this weekend / next week / specific date)
> 2. **Energy level?** (low / medium / high)
> 3. **Category?** (adventure / creative / explore / nourish / recharge / surprise me)
> 4. **Budget?** (free / budget / moderate / splurge)

### Step 3: Analyze Variety

Check `data/date-history.json` for the last 5 dates:
- Which categories have been done recently?
- Which neighborhoods visited?
- Any patterns to break?

If a category hasn't been used in the last 3 dates, suggest it:
> "You haven't done a Creative date recently - want me to include some creative options?"

### Step 4: Query Data Sources

Read city from `data/preferences.json`. Use `{city}` in all searches below.

**Data Source Priority:**
1. **WebSearch** (always available, no setup required)
2. **Ticketmaster API** (optional — only if `TICKETMASTER_API_KEY` in `~/.config/datekit/.env`)
   - Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_events.py --city "{city}" --category {cat} --days {N}`
3. **Google Places API** (optional — only if `GOOGLE_PLACES_API_KEY` in `~/.config/datekit/.env`)

**By category:**

**Adventure:**
- WebSearch: "concerts {city} this weekend", "outdoor activities {city}", "sports events {city}"
- If Ticketmaster available: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_events.py --city "{city}" --category music --days {N}`
- Check `things_to_try` list from preferences

**Creative:**
- WebSearch: "couples classes {city}", "pottery class {city}", "cooking class {city}"
- Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_classes.py --city "{city}" --category {type}`
- Check `things_to_try` list

**Explore:**
- WebSearch: "estate sales {city} this weekend", "pop-up events {city}", "flea markets {city}"
- Check `data/venues.json` museums for current exhibitions (WebSearch museum names)

**Nourish:**
- WebSearch: "best new restaurants {city}", "food festivals {city}", "{partner's favorite cuisines} restaurant {city}"
- If Google Places available: use for restaurant discovery
- Reference `favorite_cuisines` from preferences (both shared and partner-specific)

**Recharge:**
- WebSearch: "couples spa {city}", "scenic drives near {city}", "botanical gardens {city}"
- Cozy at-home ideas (cooking together, movie night)

**Surprise Me:**
- Pick the most neglected category from date history
- Mix in something from `things_to_try`

### Step 5: Generate Options

Present **3-5 concrete date plans**. Each option MUST include:

```
**Option N: [Creative Name]** (Category: [X])

**The Plan:**
- [Time] — [Activity] at [Venue/Location]
- [Time] — [Food/drinks] at [Restaurant/spot]
- [Optional: additional activity]

**Details:**
- Neighborhood: [Area]
- Estimated cost: $XX-XX
- Book/reserve: [Link or instructions]
- Why this works: [1-line connection to shared preferences]

**[Partner name] will love this because:** [Specific thing tied to their preferences]
```

### Step 6: Confirm and Log

After user picks an option (or modifies one):

1. Summarize the final plan
2. Ask: "Want me to log this to your date history?"
3. If yes, add to `data/date-history.json`:

```json
{
  "id": "date-NNN",
  "date": "YYYY-MM-DD",
  "partner": "Partner Name",
  "category": "Adventure",
  "activity": "Concert at The Metro + dinner at Thai place",
  "venues": ["venue-slug-if-applicable"],
  "neighborhood": "Neighborhood",
  "rating": null,
  "notes": "",
  "cost_estimate": 60,
  "planned_via": "date-plan"
}
```

4. Git commit: `git add data/date-history.json && git commit -m "date-planner: plan date for YYYY-MM-DD"`
5. Remind: "After the date, run `/date-plan rate` to log how it went!"

---

## Sub-commands

### `/date-plan rate`

Rate the last unrated date:

1. Read `data/date-history.json`, find last entry with `rating: null`
2. If none found: "All dates are rated! Nothing to rate."
3. Show the date details and ask:
   > How was **[activity]** on **[date]**?
   > Rating (1-10):
   > Any notes? (or skip)
4. Update the entry with rating and notes
5. Commit: `git add data/date-history.json && git commit -m "date-planner: rate date-NNN"`

### `/date-plan history`

Show date history and category analysis:

```
**Date History**

| Date | Partner | Category | Activity | Rating |
|------|---------|----------|----------|--------|
| 2026-02-08 | Jordan | Adventure | Concert + Thai food | 8/10 |
| 2026-02-02 | Sam | Explore | Estate sales + coffee | 7/10 |

**Category Balance (last 10 dates):**
- Adventure: 2 ████████
- Creative: 0
- Explore: 1 ████
- Nourish: 1 ████
- Recharge: 0

**Suggestion:** Try a Creative or Recharge date next!
```

### `/date-plan setup`

Run the onboarding flow (also re-runnable to update preferences):

**Step 1: The Basics**
> Let's set up date-planner!
>
> What's your name?

**Step 2: Partners**
> Who are you dating? Tell me their name and anything useful — food preferences, interests, things they love or hate.

(Allow multiple partners. After each one, ask "Anyone else? Say 'done' if that's it.")

Store each partner as:
```json
{
  "name": "Jordan",
  "preferences": {
    "favorite_cuisines": ["Thai", "sushi"],
    "interests": ["hiking", "live music"],
    "notes": "Loves surprises, hates being cold"
  }
}
```

**Step 3: Location**
> What city are you in?

**Step 4: Shared Preferences**
> How do you like your dates? (e.g., "spontaneous", "planned around food", "loose plan with an anchor activity")
>
> Typical budget for a date night? (free / under $30 / $30-80 / $80+)
>
> Favorite types of food?

**Step 5: Aspirations**
> Anything on your date bucket list? (things you've been wanting to try)
>
> What makes a date feel special for you? (e.g., novelty, deep conversation, physical activity, trying new food)

**Step 6: Seed Venues**

After collecting city, automatically discover venues:

1. WebSearch: "best music venues {city}", "comedy clubs {city}", "museums {city}", "popular theaters {city}"
2. For each venue found, create an entry in `data/venues.json`:
```json
{
  "slug": "venue-name-slugified",
  "name": "Venue Name",
  "category": "music|comedy|theater|museum|food",
  "subcategory": "",
  "neighborhood": "Neighborhood",
  "address": "Address if found",
  "website": "URL if found",
  "ticketing_platform": "ticketmaster|axs|direct",
  "ticketmaster_venue_id": null,
  "notes": ""
}
```
3. Add discovered venues to `data/watchlist.json` watched_venues
4. Report: "Found N venues in {city}!" with a summary list

**Step 7: Save**

1. Populate `data/preferences.json` with all collected data
2. Set `metadata.setup_complete` to true, `metadata.lastUpdated` to today
3. Git commit all data files
4. Show summary of what was saved
5. Suggest next steps:
   > You're all set! Try:
   > - `/date-plan this weekend` — plan your next date
   > - `/events` — see what's happening in {city}
   > - `/find-class cooking` — find a cooking class

---

## Category Definitions

| Category | Description | Energy | Examples |
|----------|-------------|--------|----------|
| **Adventure** | Physical, exciting, new experiences | High | Hiking, concerts, martial arts, sports |
| **Creative** | Making things, learning together | Medium | Pottery, cooking class, stained glass |
| **Explore** | Wandering, discovering new places | Medium | Estate sales, neighborhoods, markets, museums |
| **Nourish** | Food-focused quality time | Low-Med | Restaurant discovery, food tours, cooking at home |
| **Recharge** | Relaxing, low-key connection | Low | Spa, beach, movie night, scenic drives |
