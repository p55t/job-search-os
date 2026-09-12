#!/usr/bin/env python3
"""Idempotently migrate a Job Search OS SQLite tracker to schema version 20260912.

This public migration creates schema only. Instance-specific backfill of private
companies, roles, policy rows, and queue content is deliberately out of scope.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

VERSION = 20260912

APPLICATION_COLUMNS = {
    "company_key": "TEXT",
    "primary_lane": "TEXT CHECK (primary_lane IS NULL OR primary_lane IN ('infra_platform','agent_eval','incumbent_ai','other'))",
    "health_primary": "INTEGER CHECK (health_primary IS NULL OR health_primary IN (0,1))",
    "gate_outcome": "TEXT CHECK (gate_outcome IS NULL OR gate_outcome IN ('pass','fail_level','fail_ai_depth','fail_never','monitor_only'))",
    "gate_evaluated_at": "TEXT CHECK (gate_evaluated_at IS NULL OR gate_evaluated_at GLOB '????-??-??*')",
    "gate_policy_version": "TEXT",
    "ats_vendor": "TEXT",
    "discovery_channel": "TEXT CHECK (discovery_channel IS NULL OR discovery_channel IN ('direct_ats','aggregator','referral','inbound','manual'))",
    "ai_depth": "INTEGER CHECK (ai_depth IS NULL OR ai_depth BETWEEN 0 AND 2)",
    "level_band": "TEXT",
    "discovered_at": "TEXT CHECK (discovered_at IS NULL OR discovered_at GLOB '????-??-??*')",
    "discovered_by": "TEXT",
    "provenance_ref": "TEXT",
    "next_action": "TEXT",
}

OUTREACH_CONTACT_COLUMNS = {"company_key": "TEXT"}
OUTREACH_ACTION_COLUMNS = {
    "company_key": "TEXT",
    "application_id": "INTEGER REFERENCES applications(id)",
}


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def add_missing(conn: sqlite3.Connection, table: str, wanted: dict[str, str]) -> None:
    existing = columns(conn, table)
    for name, definition in wanted.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def migrate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN IMMEDIATE")
        add_missing(conn, "applications", APPLICATION_COLUMNS)
        add_missing(conn, "outreach_contacts", OUTREACH_CONTACT_COLUMNS)
        add_missing(conn, "outreach_actions", OUTREACH_ACTION_COLUMNS)

        conn.executescript(
            """
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

            CREATE INDEX IF NOT EXISTS idx_applications_company_key_status
              ON applications(company_key, status, applied_at);
            CREATE INDEX IF NOT EXISTS idx_applications_eligibility
              ON applications(status, gate_outcome, primary_lane, health_primary, ai_depth);
            CREATE INDEX IF NOT EXISTS idx_applications_discovery
              ON applications(discovery_channel, ats_vendor, discovered_at);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_url_unique
              ON applications(url) WHERE url IS NOT NULL AND trim(url) <> '';
            CREATE INDEX IF NOT EXISTS idx_company_aliases_company_key
              ON company_aliases(company_key);
            CREATE INDEX IF NOT EXISTS idx_outreach_contacts_company_key
              ON outreach_contacts(company_key);
            CREATE INDEX IF NOT EXISTS idx_outreach_actions_company_key
              ON outreach_actions(company_key);
            CREATE INDEX IF NOT EXISTS idx_outreach_actions_application_id
              ON outreach_actions(application_id);
            CREATE INDEX IF NOT EXISTS idx_discovery_runs_completed
              ON discovery_runs(run_status, completed_at DESC);

            DROP VIEW IF EXISTS applied_company_cooldowns;
            CREATE VIEW applied_company_cooldowns AS
            SELECT
              COALESCE(NULLIF(a.company_key, ''), ca.company_key, lower(trim(a.company))) AS company_key,
              min(a.company) AS company,
              max(a.applied_at) AS latest_applied_at,
              date(max(a.applied_at), '+90 day') AS cooldown_until
            FROM applications AS a
            LEFT JOIN company_aliases AS ca ON ca.alias_key = lower(trim(a.company))
            WHERE a.status = 'applied' AND a.applied_at IS NOT NULL
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
            """
        )
        conn.execute(f"PRAGMA user_version = {VERSION}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/jobsearch.db", type=Path)
    args = parser.parse_args()
    migrate(args.db)


if __name__ == "__main__":
    main()
