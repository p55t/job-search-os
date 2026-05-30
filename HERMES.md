# Hermes Integration

This guide is for users running [Hermes Agent](https://github.com/NousResearch/hermes-agent). Hermes becomes the runtime that executes the OS — ingest, query, lint, apply are skill-driven.

## Install

```bash
mkdir -p ~/.hermes/workspace
cd ~/.hermes/workspace
git clone https://github.com/<you>/job-search-os.git
cd job-search-os

# Create the private layer (gitignored)
mkdir -p sources/{job-posts,company-news,user-docs,interviews,outreach}
mkdir -p wiki/{profile,companies,roles,jobs,outreach,interviews,evidence,resumes}

# Initialize the profile (this is your single source of truth)
cp templates/profile.md wiki/profile/me.md
$EDITOR wiki/profile/me.md
```

## The skill

Install the companion skill at `~/.hermes/skills/job-search/job-search-os/SKILL.md`. A minimal version:

```markdown
---
name: job-search-os
description: Operate the user's Job Search OS — a markdown wiki + SQLite tracker for job applications, outreach, interviews, and resumes. Loads when the user mentions jobs, applications, outreach, resumes, interviews, or specific target companies.
version: 1.0.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [job-search, productivity, knowledge-base]
---

# Job Search OS

The workspace lives at `~/.hermes/workspace/job-search-os/`.

Before doing anything, read `SCHEMA.md` to load the conventions. Then read `wiki/profile/me.md` to load the human's profile.

For each user request, follow the matching op in `ops/`:
- new job posting → `ops/ingest.md` + `ops/apply.md`
- "what should I do today" → `ops/lint.md` + `ops/query.md`
- a question about the human's background → `ops/query.md`
- resume generation → `ops/apply.md` (§ resume)

## PII boundary

Never commit anything from `sources/` or `wiki/` to git. These dirs are gitignored. Only the schema (templates, ops, prompts) is in git. If the user asks you to push changes, only push files at the repo root or under `ops/`, `templates/`, `prompts/`, `data/schema.sql`, or `examples/`.
```

## Daily flow

1. **New role surfaced** — user pastes a URL or job description in Discord.
   - Hermes saves the source under `sources/job-posts/`.
   - Runs `ops/ingest.md` — updates `wiki/companies/{co}.md`, creates `wiki/jobs/{date}-{co}-{slug}.md`.
   - Replies with the fit score and recommended next action.

2. **Apply** — user says "apply to that."
   - Hermes runs `ops/apply.md` — drafts a resume in `wiki/resumes/`, picks evidence pages.
   - Returns the resume markdown for review.

3. **Outreach** — user says "who do we know at Cohere?"
   - Hermes runs `ops/query.md` against `wiki/outreach/` + `wiki/companies/cohere.md`.
   - Returns a ranked list with last-touch dates.

4. **Weekly lint** — user says "let's review where we are."
   - Hermes runs `ops/lint.md` — stale pages, orphans, broken links, contradictions.
   - Returns a punch list.

## Federation across Hermes nodes

If you run multiple Hermes nodes (e.g. laptop + home server), the job-search workspace can be synced via git to a private repo or any file-sync layer. The schema repo stays public; the user-data repo stays private.
