# Op: Lint

Periodic health check on the wiki. Surface decay before it compounds.

## When this runs

- The human says "let's review where we are" / "weekly check" / "what's stale."
- Automatically at the start of any session if the last lint was >7 days ago.
- Before any large operation (e.g. before generating a resume, lint the relevant evidence pages).

## Checks

### 1. Stale

A page is **stale** if its `Last verified` date is more than 8 weeks ago. Templates expose a `Last verified:` field — keep it honest.

- `wiki/companies/*` go stale fastest (orgs reorg, roles open and close)
- `wiki/profile/me.md` stale = the human's current job/responsibilities may have changed
- `wiki/evidence/*` are usually evergreen (a story from 2023 is still a story)

Report: `<count>` stale pages, list paths.

### 2. Orphans

A wiki page with **zero inbound links** from other wiki pages. Either:

- It should be linked from somewhere (e.g. a `job` page that no `resume` page references)
- Or it should be deleted (overcome by events)

Report: list orphans + best guess at the right inbound link.

### 3. Broken cross-links

A markdown link `[X](../path)` where the target file no longer exists.

Report: link source page + dead target.

### 4. Contradictions

Search for the marker `**CONTRADICTION` across `wiki/`.

Report: every active contradiction with a one-line summary.

### 5. Missing core pages

These pages should always exist:

- `wiki/profile/me.md`
- `wiki/profile/positioning.md`

If either is missing, report it as critical.

### 6. Pipeline freshness (optional, if using SQLite)

Query `data/jobsearch.db`:

- Applications in `status='applied'` with no follow-up logged in 14 days → flag for follow-up.
- Outreach contacts last_touch >30 days, status not closed → flag for re-warm.

## Output

Single message, ordered:

```
LINT REPORT — YYYY-MM-DD

Critical (must fix):
  - <items>

High (this week):
  - <items>

Medium (this month):
  - <items>

OK:
  <count> pages clean
```

Do **not** auto-fix. The human resolves each item. Lint surfaces, it doesn't decide.
