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

## Architecture

Inspired by [Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Four layers:

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
│  evidence · resumes · queue · interviews                        │
│  Every page ends with [[wikilinks]] in a ## Related section     │
└─────────────────────────────────────────────────────────────────┘
                      │
          ┌───────────┴────────────┐
          ▼                        ▼
┌──────────────────┐    ┌──────────────────────────────────────┐
│  FTS5 SEARCH     │    │  OBSIDIAN GRAPH VIEW (laptop)        │
│  data/wiki-      │    │  Synced via Syncthing · local vault  │
│  index.db        │    │  [[wikilinks]] render as graph edges │
│  Rebuilt every   │    │  Filter: exclude sources/            │
│  30 min by cron  │    └──────────────────────────────────────┘
└──────────────────┘
          │ agent queries
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  SQLITE TRACKER  (optional, gitignored)                         │
│  data/jobsearch.db — application state, outreach pipeline       │
└─────────────────────────────────────────────────────────────────┘
```

### How the agent navigates the wiki

1. **Bootstrap every session:** read `SCHEMA.md` → `wiki/profile/me.md` → `wiki/profile/positioning.md`
2. **Search:** query `data/wiki-index.db` (FTS5) for ranked, relevant pages — one SQL call instead of grepping 50 files
3. **Navigate:** follow `[[wikilinks]]` in each page's `## Related` section to pull connected context
4. **Write:** every new/updated wiki page gets a `## Related` section with `[[wikilinks]]` — keeps the graph connected and the index fresh

### Obsidian sync

The wiki lives on a Hermes/LXC host. For daily reading/navigation on a laptop:

```
host wiki/ ──Syncthing──▶ ~/syncthing/job-search-os/   ← open as Obsidian vault
                          ~/syncthing/job-search-private/ (private layer)
```

Open `~/syncthing/` as a single Obsidian vault. In Graph View, exclude `sources/` and `src/` to see only the connected wiki.


