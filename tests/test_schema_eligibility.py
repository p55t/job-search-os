#!/usr/bin/env python3
"""Smoke tests for the public 20260912 SQLite eligibility schema."""
from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'data/schema.sql'
MIGRATION = ROOT / 'data/migrations/20260912_schema_eligibility.py'


def test_fresh_schema() -> None:
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / 'fresh.db'
        conn = sqlite3.connect(db)
        conn.executescript(SCHEMA.read_text())
        version = conn.execute('PRAGMA user_version').fetchone()[0]
        assert version == 20260912
        conn.execute(
            "INSERT INTO applications (company,company_key,role,url,status,primary_lane,health_primary,gate_outcome,gate_evaluated_at,gate_policy_version,ats_vendor,discovery_channel,ai_depth,level_band,discovered_at,discovered_by,provenance_ref) "
            "VALUES ('Example Co','example','Staff PM','https://example.test/role','scored','infra_platform',0,'pass','2026-09-12T00:00:00Z','test','Example ATS','direct_ats',2,'staff','2026-09-12','test','test')"
        )
        assert conn.execute('SELECT count(*) FROM v_eligible_apply_now').fetchone()[0] == 1
        conn.execute("INSERT INTO applications (company,company_key,role,status,applied_at) VALUES ('Example Co','example','Old role','applied','2026-09-12')")
        assert conn.execute('SELECT count(*) FROM v_eligible_apply_now').fetchone()[0] == 0
        conn.close()


def test_legacy_migration_is_idempotent() -> None:
    legacy = """
    CREATE TABLE applications (id INTEGER PRIMARY KEY, company TEXT NOT NULL, role TEXT NOT NULL, url TEXT, source TEXT, status TEXT NOT NULL DEFAULT 'new', wiki_page TEXT, applied_at TEXT, next_action_at TEXT, notes TEXT);
    CREATE TABLE outreach_contacts (id INTEGER PRIMARY KEY, person_name TEXT NOT NULL, title TEXT, company TEXT NOT NULL, connection_strength INTEGER, source TEXT, last_touch TEXT, wiki_page TEXT, notes TEXT);
    CREATE TABLE outreach_actions (id INTEGER PRIMARY KEY, contact_id INTEGER, company TEXT NOT NULL, role TEXT, channel TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', message_draft TEXT, artifact_ref TEXT, sent_at TEXT, followup_at TEXT, replied_at TEXT, outcome TEXT);
    """
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / 'legacy.db'
        conn = sqlite3.connect(db)
        conn.executescript(legacy)
        conn.close()
        command = [sys.executable, str(MIGRATION), '--db', str(db)]
        subprocess.check_call(command)
        subprocess.check_call(command)
        conn = sqlite3.connect(db)
        columns = {row[1] for row in conn.execute('PRAGMA table_info(applications)')}
        assert {'company_key', 'primary_lane', 'health_primary', 'gate_outcome', 'next_action'} <= columns
        assert conn.execute('PRAGMA user_version').fetchone()[0] == 20260912
        assert conn.execute("SELECT count(*) FROM sqlite_master WHERE type='view' AND name='v_eligible_apply_now'").fetchone()[0] == 1
        conn.close()


if __name__ == '__main__':
    test_fresh_schema()
    test_legacy_migration_is_idempotent()
    print('schema eligibility tests: PASS')
