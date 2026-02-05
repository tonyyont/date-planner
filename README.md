# date-planner

A Claude Code skill for planning dates. Works in any city. Finds real events, restaurants, and activities personalized to your relationship(s).

Supports couples and people dating multiple people.

## Install

```bash
git clone https://github.com/tonyyont/date-planner.git
cd date-planner
```

Open the folder in Claude Code (CLI or desktop app) and say anything — it'll start setup automatically.

<details>
<summary>Alternative: Claude Code plugin marketplace (CLI only)</summary>

If you use the Claude Code CLI and want the skills available globally:

```
/plugin marketplace add https://github.com/tonyyont/date-planner.git
/plugin install date-planner@tonyyont-date-planner
```

Note: Use the full HTTPS URL, not the `owner/repo` shorthand ([known SSH issue](https://github.com/anthropics/claude-code/issues/9719)).
</details>

## Getting Started

Open the project in Claude Code and send any message. First run walks you through setup (~2 min):
- Your name and who you're dating
- Your city
- Food preferences, date style, budget
- Things you want to try

It then auto-discovers popular venues in your city.

## Skills

| Skill | What it does |
|-------|-------------|
| `/date-plan` | Plan a date with concrete options |
| `/events` | Find events in your city |
| `/venue-watch` | Track venues and artists |
| `/find-class` | Find classes and experiences |

## How it works

1. **Setup**: Tell it about yourselves — names, city, food prefs, date style
2. **Plan**: Get 3-5 concrete date options with real venues, times, and costs
3. **Track**: Log dates, rate them, see your category balance
4. **Grow**: Your venue list and preferences evolve as you use it

## Optional: API Keys

date-planner works out of the box using web search. For richer event data:

### Ticketmaster (free)
Better structured music and theater results.

```bash
mkdir -p ~/.config/datekit
echo 'TICKETMASTER_API_KEY=your-key-here' > ~/.config/datekit/.env
```

Get a free key at https://developer.ticketmaster.com

### Google Places (free $200/month credit)
Restaurant discovery with ratings and hours.

```bash
echo 'GOOGLE_PLACES_API_KEY=your-key-here' >> ~/.config/datekit/.env
```

## Date Categories

| Category | Energy | Examples |
|----------|--------|----------|
| Adventure | High | Hiking, concerts, martial arts, sports |
| Creative | Medium | Pottery, cooking class, stained glass |
| Explore | Medium | Estate sales, neighborhoods, museums, markets |
| Nourish | Low-Med | Restaurant discovery, food tours, cooking together |
| Recharge | Low | Spa, beach, movie night, scenic drives |
