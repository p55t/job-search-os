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

## Architecture — the LLM Wiki pattern

Inspired by [Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Three layers:

```
┌───────────────────────────────────────────────────────┐
│  SOURCES  (immutable)                                 │
│  Raw inputs: job posts, company news, your own docs,  │
│  interview transcripts, referral emails, LinkedIn DMs │
└───────────────────────────────────────────────────────┘
                      │
                      ▼ ingest
┌───────────────────────────────────────────────────────┐
│  WIKI  (LLM-maintained markdown)                      │
│  One page per entity, heavily cross-linked            │
│  profile, companies, roles, jobs, outreach,           │
│  interviews, evidence (story bank), resumes           │
└───────────────────────────────────────────────────────┘
                      │
                      ▼ guides
┌───────────────────────────────────────────────────────┐
│  SCHEMA  (this repo)                                  │
│  SCHEMA.md — conventions, page types, cross-link rules│
│  ops/      — ingest, query, lint, apply workflows     │
│  templates/— skeleton for each page type              │
│  prompts/  — voice and style rules                    │
└───────────────────────────────────────────────────────┘
```

Three operations on the wiki:

- **Ingest** — add a source, update affected pages, flag contradictions
- **Query** — answer a question by searching the wiki, optionally file the answer as a new page
- **Lint** — find stale pages, broken cross-links, orphans, contradictions

## Two-repo split

This repo holds the **schema** only. Your actual search data is split:

| Layer    | Lives in                       | Contains                                    |
|----------|--------------------------------|---------------------------------------------|
| Schema   | this repo                      | conventions, templates, prompts, ops        |
| Sources  | your machine (`sources/`)      | raw, immutable inputs                       |
| Wiki     | your machine (`wiki/`)         | LLM-maintained pages with your real data    |

`.gitignore` ensures `sources/` and `wiki/` never ship to git. Your PII stays on your machine.

## Quickstart with Hermes Agent

If you're running [Hermes Agent](https://github.com/NousResearch/hermes-agent):

```bash
# Clone the schema into your Hermes workspace
mkdir -p ~/.hermes/workspace
cd ~/.hermes/workspace
git clone https://github.com/<you>/job-search-os.git
cd job-search-os

# Bootstrap your sources and wiki
mkdir -p sources/{job-posts,company-news,user-docs,interviews,outreach}
mkdir -p wiki/{profile,companies,roles,jobs,outreach,interviews,evidence,resumes}
cp templates/profile.md wiki/profile/me.md
$EDITOR wiki/profile/me.md   # fill in your actual profile
```

Then install the companion Hermes skill (see [`HERMES.md`](HERMES.md)) and chat with your bot:

> "I want to apply to <https://job-url>. Score it and draft a tailored resume."

The bot runs the `apply` op against your wiki and reports back.

## Quickstart without Hermes

You can use any LLM with file access (Claude Code, Cursor, plain Claude with file uploads). Point it at this repo plus your `sources/` and `wiki/` dirs. The agent reads [`SCHEMA.md`](SCHEMA.md) to learn the conventions, then operates per [`ops/`](ops/).

## Layout

```
SCHEMA.md           the operating manual — read this first
HERMES.md           Hermes-specific integration
ops/                workflows: ingest, query, lint, apply
templates/          skeletons for each wiki page type
prompts/            voice, style, anti-slop, resume rules
data/schema.sql     optional SQLite tracker schema
examples/           sanitized example pages
sources/.gitkeep    your raw inputs go here (gitignored)
wiki/.gitkeep       your LLM-maintained wiki goes here (gitignored)
```

## Design rules

1. **One entity per page.** A company is one page. A job is one page. A contact is one page. Pages link to each other; they don't duplicate each other.
2. **Sources are immutable.** Never edit a file in `sources/`. Update the wiki instead.
3. **Verified facts only in resumes.** Every metric in a generated resume traces back to an evidence-bank page or a source. No invented numbers.
4. **The schema is small.** If you can't keep it in your head, it's too big.

## License

MIT — fork it, rewrite it, make it yours.
