-- Canonical SQLite state tracker for Job Search OS.
-- The database file is private and gitignored; this is the public fresh-install schema.
-- Store dates/timestamps in ISO-8601 form.

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL,
  company_key TEXT NOT NULL,
  role TEXT NOT NULL,
  url TEXT,
  source TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  wiki_page TEXT,
  applied_at TEXT CHECK (applied_at IS NULL OR applied_at GLOB '????-??-??'),
  next_action TEXT,
  next_action_at TEXT CHECK (next_action_at IS NULL OR next_action_at GLOB '????-??-??*'),
  primary_lane TEXT CHECK (primary_lane IS NULL OR primary_lane IN ('infra_platform','agent_eval','incumbent_ai','other')),
  health_primary INTEGER CHECK (health_primary IS NULL OR health_primary IN (0,1)),
  gate_outcome TEXT CHECK (gate_outcome IS NULL OR gate_outcome IN ('pass','fail_level','fail_ai_depth','fail_never','monitor_only')),
  gate_evaluated_at TEXT CHECK (gate_evaluated_at IS NULL OR gate_evaluated_at GLOB '????-??-??*'),
  gate_policy_version TEXT,
  ats_vendor TEXT,
  discovery_channel TEXT CHECK (discovery_channel IS NULL OR discovery_channel IN ('direct_ats','aggregator','referral','inbound','manual')),
  ai_depth INTEGER CHECK (ai_depth IS NULL OR ai_depth BETWEEN 0 AND 2),
  level_band TEXT,
  discovered_at TEXT CHECK (discovered_at IS NULL OR discovered_at GLOB '????-??-??*'),
  discovered_by TEXT,
  provenance_ref TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS briefs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  summary TEXT NOT NULL,
  wiki_page TEXT
);

CREATE TABLE IF NOT EXISTS outreach_contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_name TEXT NOT NULL,
  title TEXT,
  company TEXT NOT NULL,
  company_key TEXT,
  connection_strength INTEGER CHECK(connection_strength BETWEEN 1 AND 5),
  source TEXT,
  last_touch TEXT,
  wiki_page TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS outreach_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER REFERENCES outreach_contacts(id),
  application_id INTEGER REFERENCES applications(id),
  company TEXT NOT NULL,
  company_key TEXT,
  role TEXT,
  channel TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  message_draft TEXT,
  artifact_ref TEXT,
  sent_at TEXT,
  followup_at TEXT,
  replied_at TEXT,
  outcome TEXT
);

CREATE TABLE IF NOT EXISTS company_aliases (
  alias_key TEXT PRIMARY KEY,
  company_key TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS company_policy (
  company_key TEXT PRIMARY KEY,
  discovery_policy TEXT NOT NULL DEFAULT 'eligible'
    CHECK (discovery_policy IN ('eligible','monitor_only','exclude')),
  policy_reason TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS discovery_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_key TEXT NOT NULL UNIQUE,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  run_kind TEXT NOT NULL CHECK (run_kind IN ('daily','rotating','manual','backfill')),
  run_status TEXT NOT NULL DEFAULT 'running'
    CHECK (run_status IN ('running','success','partial','failed')),
  roles_evaluated INTEGER NOT NULL DEFAULT 0 CHECK (roles_evaluated >= 0),
  gate_pass_count INTEGER NOT NULL DEFAULT 0 CHECK (gate_pass_count >= 0),
  fail_level_count INTEGER NOT NULL DEFAULT 0 CHECK (fail_level_count >= 0),
  fail_ai_depth_count INTEGER NOT NULL DEFAULT 0 CHECK (fail_ai_depth_count >= 0),
  fail_never_count INTEGER NOT NULL DEFAULT 0 CHECK (fail_never_count >= 0),
  monitor_only_count INTEGER NOT NULL DEFAULT 0 CHECK (monitor_only_count >= 0),
  net_new_count INTEGER NOT NULL DEFAULT 0 CHECK (net_new_count >= 0),
  duplicate_count INTEGER NOT NULL DEFAULT 0 CHECK (duplicate_count >= 0),
  cooldown_suppressed_count INTEGER NOT NULL DEFAULT 0 CHECK (cooldown_suppressed_count >= 0),
  notes TEXT,
  CHECK (roles_evaluated = gate_pass_count + fail_level_count + fail_ai_depth_count + fail_never_count + monitor_only_count),
  CHECK (net_new_count <= gate_pass_count)
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_next_action ON applications(next_action_at);
CREATE INDEX IF NOT EXISTS idx_applications_company_status ON applications(company, status, applied_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_wiki_page_unique ON applications(wiki_page) WHERE wiki_page IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_url_unique ON applications(url) WHERE url IS NOT NULL AND trim(url) <> '';
CREATE INDEX IF NOT EXISTS idx_applications_company_key_status ON applications(company_key, status, applied_at);
CREATE INDEX IF NOT EXISTS idx_applications_eligibility ON applications(status, gate_outcome, primary_lane, health_primary, ai_depth);
CREATE INDEX IF NOT EXISTS idx_applications_discovery ON applications(discovery_channel, ats_vendor, discovered_at);
CREATE INDEX IF NOT EXISTS idx_outreach_last_touch ON outreach_contacts(last_touch);
CREATE INDEX IF NOT EXISTS idx_outreach_contacts_company_key ON outreach_contacts(company_key);
CREATE INDEX IF NOT EXISTS idx_outreach_actions_company_key ON outreach_actions(company_key);
CREATE INDEX IF NOT EXISTS idx_outreach_actions_application_id ON outreach_actions(application_id);
CREATE INDEX IF NOT EXISTS idx_company_aliases_company_key ON company_aliases(company_key);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_completed ON discovery_runs(run_status, completed_at DESC);

DROP VIEW IF EXISTS applied_company_cooldowns;
CREATE VIEW applied_company_cooldowns AS
SELECT
  COALESCE(NULLIF(a.company_key, ''), ca.company_key, lower(trim(a.company))) AS company_key,
  min(a.company) AS company,
  max(a.applied_at) AS latest_applied_at,
  date(max(a.applied_at), '+90 day') AS cooldown_until
FROM applications AS a
LEFT JOIN company_aliases AS ca ON ca.alias_key = lower(trim(a.company))
WHERE a.applied_at IS NOT NULL
  AND a.status IN ('applied','rejected','screen','onsite','offer','withdrew')
GROUP BY COALESCE(NULLIF(a.company_key, ''), ca.company_key, lower(trim(a.company)));

DROP VIEW IF EXISTS v_eligible_apply_now;
CREATE VIEW v_eligible_apply_now AS
SELECT a.*
FROM applications AS a
LEFT JOIN company_policy AS p ON p.company_key = a.company_key
LEFT JOIN applied_company_cooldowns AS c ON c.company_key = a.company_key
WHERE a.status IN ('new','scored')
  AND a.gate_outcome = 'pass'
  AND a.primary_lane IN ('infra_platform','agent_eval','incumbent_ai')
  AND a.health_primary IS NOT 1
  AND a.ai_depth BETWEEN 1 AND 2
  AND a.level_band IN ('senior','staff','principal','technical')
  AND a.url IS NOT NULL AND trim(a.url) <> ''
  AND COALESCE(p.discovery_policy, 'eligible') = 'eligible'
  AND (c.company_key IS NULL OR c.cooldown_until < date('now'));

CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
  path, title, section, type, content, tokenize='porter ascii'
);

CREATE TABLE IF NOT EXISTS wiki_meta (
  path TEXT PRIMARY KEY,
  title TEXT,
  type TEXT,
  related TEXT,
  indexed_at TEXT
);

PRAGMA user_version = 20260913;
