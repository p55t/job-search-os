-- Canonical SQLite state tracker for the Job Search OS.
--
-- The wiki holds context; this database holds state transitions.
-- `data/jobsearch.db` is the source of truth for application state,
-- applied/archive records, follow-up dates, and company cooldown derivation.
-- The database file (`data/jobsearch.db`) is gitignored.
-- Store dates as ISO-8601 calendar dates: YYYY-MM-DD.

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  url TEXT,
  source TEXT,
  status TEXT NOT NULL DEFAULT 'new',  -- new | scored | applied | screen | onsite | offer | rejected | withdrew
  wiki_page TEXT,                       -- e.g. wiki/jobs/2026-05-30-exampleco-pm-growth.md
  applied_at TEXT CHECK (applied_at IS NULL OR applied_at GLOB '????-??-??'),
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
CREATE INDEX IF NOT EXISTS idx_applications_company_status ON applications(company, status, applied_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_wiki_page_unique
  ON applications(wiki_page) WHERE wiki_page IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_outreach_last_touch ON outreach_contacts(last_touch);

-- Derived company cooldowns. Agents should use this view before surfacing
-- application recommendations; aliases still need human/agent judgment for
-- cases like Cursor/Anysphere.
DROP VIEW IF EXISTS applied_company_cooldowns;
CREATE VIEW applied_company_cooldowns AS
SELECT
  lower(trim(company)) AS company_key,
  min(company) AS company,
  max(applied_at) AS latest_applied_at,
  date(max(applied_at), '+90 day') AS cooldown_until
FROM applications
WHERE status='applied' AND applied_at IS NOT NULL
GROUP BY lower(trim(company));

-- FTS5 full-text search index over wiki pages.
-- Populated by scripts/wiki.py index.
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
