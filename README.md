# Job Search OS

**A single-user operating system for running a focused, honest, interview-generating job search through an LLM agent.**

Job Search OS is not an app. It's a **knowledge architecture** — a set of conventions for how an AI agent (Hermes, Claude, or any LLM with file access) should organize your job search as a living wiki that compounds over time.

The repo contains the **operating manual**. Your actual search data lives privately on your own machine.

## Philosophy

Most job-search tools optimize for volume. This one optimizes for signal.

- Prioritize roles that actually fit.
- Use referrals and proof-of-work before cold applications.
- Write like a real person.
- Keep one source of truth per entity (you, each company, each role, each contact).
- Let the AI maintain cross-references; humans curate sources and direction.

## Operating model

- `prompts/` captures reusable instructions for skill capture and short experiments.
- `wiki/ops/` holds the stable operating contract and the change log.
- `wiki/strategies/` holds the current best playbook.
- `wiki/comparisons/` holds decision guides.
- If a workflow repeats often enough to be worth automation, capture it as a Hermes skill and mirror the recipe here.

## Architecture

Inspired by [Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). The operating model is:

```
┌─────────────────────────────────────────────────────────────────┐
│  SOURCES  (immutable raw inputs)                                │
│  job posts · company news · your docs · transcripts · DMs      │
└─────────────────────────────────────────────────────────────────┘
                      │ ingest (ops/ingest.md)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  WIKI  (LLM-maintained, gitignored)                             │
│  profile · positioning · companies · jobs · outreach           │
│  evidence · resumes · queue · interviews · strategies          │
│  ops · comparisons                                              │
│  Every page ends with [[wikilinks]] in a ## Related section     │
└─────────────────────────────────────────────────────────────────┘
                      │
          ┌───────────┴────────────┐
          │                        │
          ▼                        ▼
┌────────────────────────┐   ┌────────────────────────────────────┐
│  GENERATED NAVIGATION  │   │  FTS5 SEARCH                        │
│  wiki/INDEX.md         │   │  data/wiki-index.db                │
│  wiki/aliases.md       │   │  Rebuilt every 30 min by cron      │
│  scripts/wiki.py index │   │  Query from the CLI or SQLite      │
│  scripts/wiki.py lint  │   └────────────────────────────────────┘
└────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  SQLITE TRACKER  (canonical state, gitignored)                  │
│  data/jobsearch.db — application state, outreach pipeline       │
└─────────────────────────────────────────────────────────────────┘
```

### How the agent navigates the wiki

1. **Bootstrap every session:** read `SCHEMA.md` → `wiki/ops/source-of-truth.md` → `wiki/profile/me.md` → `wiki/profile/positioning.md`.
2. **Check state first:** query `data/jobsearch.db` and `applied_company_cooldowns` before recommending or changing a role; the queue is a rendered view.
3. **Navigate first:** open `wiki/INDEX.md` to find the relevant company/role/evidence pages.
4. **Alias-resolve:** use `wiki/aliases.md` when a company or role is referred to by a customer-facing name.
5. **Search:** query `data/wiki-index.db` (FTS5) for ranked, relevant pages when the index is not enough.
6. **Write:** record state transitions in SQLite before reconciling `wiki/queue/target-queue.md`; every new/updated wiki page gets a `## Related` section with `[[wikilinks]]`.
7. **Promote reusable work:** keep current-best-practice guidance in `wiki/strategies/`, record decisions and change outcomes in `wiki/ops/change-log.md`, and only export a Hermes skill when the workflow is stable enough to reuse outside the repo.

### Private-state bootstrap

The repository intentionally does not contain job-search data. Create the private tracker once before using stateful workflows:

```bash
sqlite3 data/jobsearch.db < data/schema.sql
```

Create `wiki/ops/source-of-truth.md` from `templates/source-of-truth.md` and fill it with the private operating contract. Do not commit the resulting wiki page.

### Obsidian sync

The wiki lives on a Hermes/LXC host. For daily reading/navigation on a laptop:

```
host wiki/ ──Syncthing──▶ ~/syncthing/job-search-os/   ← open as Obsidian vault
                          ~/syncthing/job-search-private/ (private layer)
```

Open `~/syncthing/` as a single Obsidian vault. In Graph View, exclude `sources/` and `src/` to see only the connected wiki.


