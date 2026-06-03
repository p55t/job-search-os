-- Optional SQLite tracker for the Job Search OS.
--
-- The wiki holds context; this database holds state transitions.
-- Use either, both, or neither. The database file (`data/jobsearch.db`) is
-- gitignored.

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  url TEXT,
  source TEXT,
  status TEXT NOT NULL DEFAULT 'new',  -- new | scored | applied | screen | onsite | offer | rejected | withdrew
  wiki_page TEXT,                       -- e.g. wiki/jobs/2026-05-30-exampleco-pm-growth.md
  applied_at TEXT,
  next_action_at TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS briefs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  summary TEXT NOT NULL,
  wiki_page TEXT                        -- optional pointer to a `wiki/` page
);

CREATE TABLE IF NOT EXISTS outreach_contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_name TEXT NOT NULL,
  title TEXT,
  company TEXT NOT NULL,
  connection_strength INTEGER CHECK(connection_strength BETWEEN 1 AND 5),
  source TEXT,
  last_touch TEXT,
  wiki_page TEXT,                       -- e.g. wiki/outreach/{slug}.md
  notes TEXT
);

CREATE TABLE IF NOT EXISTS outreach_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER REFERENCES outreach_contacts(id),
  company TEXT NOT NULL,
  role TEXT,
  channel TEXT NOT NULL,                -- linkedin | email | referral | conference | other
  status TEXT NOT NULL DEFAULT 'draft', -- draft | sent | replied | dead
  message_draft TEXT,
  artifact_ref TEXT,                    -- e.g. wiki/resumes/{slug}.md
  sent_at TEXT,
  followup_at TEXT,
  replied_at TEXT,
  outcome TEXT
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_next_action ON applications(next_action_at);
CREATE INDEX IF NOT EXISTS idx_outreach_last_touch ON outreach_contacts(last_touch);

-- FTS5 full-text search index over wiki pages.
-- Populated by scripts/build-wiki-index.py (runs via Hermes cron every 30 min).
-- Query: SELECT path, title, snippet(wiki_fts,4,'→','←','...',20) FROM wiki_fts WHERE wiki_fts MATCH 'query' ORDER BY rank;
CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
  path,        -- relative path from workspace root
  title,       -- H1 heading or derived title
  section,     -- H2/H3 heading this chunk belongs to
  type,        -- companies | evidence | resumes | profile | outreach | queue | other
  content,     -- stripped markdown text
  tokenize='porter ascii'
);

CREATE TABLE IF NOT EXISTS wiki_meta (
  path TEXT PRIMARY KEY,
  title TEXT,
  type TEXT,
  related TEXT,         -- raw ## Related block for quick link lookup
  indexed_at TEXT
);
