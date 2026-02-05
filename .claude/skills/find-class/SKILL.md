---
name: find-class
description: Find classes and experiences — martial arts, cooking, pottery, and more
---

# Find Class Skill

Find classes, workshops, and experiences for date activities.

## Usage

- `/find-class` - Browse available categories
- `/find-class martial-arts` - Find martial arts intro classes
- `/find-class cooking` - Find cooking classes
- `/find-class pottery` - Find pottery/ceramics
- `/find-class art` - Find art classes (paint & sip, stained glass, etc.)
- `/find-class [custom query]` - Search for anything

## Workflow

### Step 0: Setup Check

Read `data/preferences.json`. If `metadata.setup_complete` is false, say:
> "Run `/date-plan setup` first to set your city and preferences!"

### Step 1: Determine Category

Read city from `data/preferences.json`.
Read `things_to_try` from `data/preferences.json` for contextual reminders.

If no arguments, show menu:

> **Find a Class!**
>
> Categories:
> 1. **Martial Arts** — BJJ, taekwondo, kickboxing intro classes
> 2. **Cooking** — Various cuisines, pasta making, date night cooking
> 3. **Pottery** — Ceramics, wheel throwing
> 4. **Art** — Paint & sip, stained glass, drawing
> 5. **Other** — Tell me what you're interested in

If any `things_to_try` items match the category, add a reminder:
> *From your bucket list: [matching item]*

### Step 2: Generate Search Queries

Run the query generator:
```bash
python3 scripts/fetch_classes.py --city "{city}" --category {category} --format json
```

This outputs:
- `search_queries`: list of optimized search strings for the city
- `platforms`: list of class discovery platforms with URLs

### Step 3: Execute Web Searches

Use WebSearch with each query from the script output.

Also check these platforms for the category:
- **ClassBento** (classbento.com) — Creative classes
- **Coursehorse** (coursehorse.com) — All types
- **Airbnb Experiences** — Unique local experiences
- **Groupon** — Deals on classes and activities

### Step 4: Present Options

Format results clearly:

```
## [Category] Classes in [City]

### 1. [Class Name] at [Studio/Location]
- **Type**: Drop-in / Series / Private lesson
- **Duration**: X hours
- **Cost**: $XX (intro/trial: $XX if available)
- **Schedule**: [days and times]
- **Location**: [Neighborhood, address]
- **Couples-friendly**: Yes/No
- **Book**: [URL]
- **Notes**: [relevant details]

### 2. [Class Name] at [Studio/Location]
...
```

### Step 5: Offer Next Steps

> **What next?**
> - Turn this into a full date plan (with food pairing) → `/date-plan creative`
> - Save for later → I'll add to your things-to-try list
> - Book now → [Direct link]

If user wants to save for later:
1. Add to `data/preferences.json` `things_to_try` list
2. Git commit: `git add data/preferences.json && git commit -m "date-planner: add [class] to things-to-try"`

## Error Handling

- If WebSearch returns few results: try broader queries, check platforms directly
- Always present at least the platform URLs so user can browse manually
- If city is small, expand search radius: "classes near {city}"
