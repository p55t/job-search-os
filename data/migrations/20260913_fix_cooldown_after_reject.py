#!/usr/bin/env python3
"""Repair submitted-company cooldowns after terminal application outcomes.

This public migration changes only the cooldown view. A row contributes to the
90-day cooldown when it has a confirmed `applied_at` submission date and a
submitted/process status; unsubmitted scored/new rows remain excluded.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

PREVIOUS_VERSION = 20260912
VERSION = 20260913

COOLDOWN_VIEW_SQL = """
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
"""


def migrate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version == VERSION:
            return
        if current_version != PREVIOUS_VERSION:
            raise RuntimeError(
                f"expected user_version {PREVIOUS_VERSION}, found {current_version}; refusing migration"
            )

        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DROP VIEW IF EXISTS v_eligible_apply_now")
        conn.execute("DROP VIEW IF EXISTS applied_company_cooldowns")
        conn.execute(COOLDOWN_VIEW_SQL)
        conn.execute(
            """
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
              AND (c.company_key IS NULL OR c.cooldown_until < date('now'))
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
