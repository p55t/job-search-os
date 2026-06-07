from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from textwrap import shorten

ROOT = Path(__file__).resolve().parents[2]
KB = ROOT / "kb"
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"
DB = DATA / "jobsearch.db"
SCHEMA = DATA / "schema.sql"
COMPANIES_FILE = KB / "companies" / "monitoring.md"
OUTREACH_LOG = KB / "outreach" / "TRACKER.md"


DEFAULT_COMPANIES = [
    "Amazon / AWS",
    "Microsoft",
    "Meta",
    "Google",
    "OpenAI",
    "Anthropic",
    "Toast",
    "Babylist",
    "Gradial",
    "Pulley",
    "Cority",
]


def cmd_init(_: argparse.Namespace) -> int:
    for path in [
        KB / "evidence",
        KB / "stories",
        KB / "companies",
        KB / "jobs",
        KB / "interviews",
        KB / "resumes",
        KB / "outreach",
        DATA,
        PROMPTS,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    if SCHEMA.exists():
        with sqlite3.connect(DB) as conn:
            conn.executescript(SCHEMA.read_text())

    if not COMPANIES_FILE.exists():
        COMPANIES_FILE.write_text(
            "# Target companies\n\n"
            "Starter watchlist. Edit freely.\n\n"
            + "\n".join(f"- {name}" for name in DEFAULT_COMPANIES)
            + "\n"
        )
    print("initialized")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    print(f"root: {ROOT}")
    print(f"kb: {KB.exists()}")
    print(f"data: {DATA.exists()}")
    print(f"prompts: {PROMPTS.exists()}")
    print(f"db: {DB.exists()}")
    print(f"targets: {COMPANIES_FILE.exists()}")
    print(f"outreach_tracker: {OUTREACH_LOG.exists()}")
    with connect() as conn:
        outreach_contacts = conn.execute("SELECT COUNT(*) AS n FROM outreach_contacts").fetchone()["n"]
        outreach_actions = conn.execute("SELECT COUNT(*) AS n FROM outreach_actions").fetchone()["n"]
        open_followups = conn.execute(
            "SELECT COUNT(*) AS n FROM outreach_actions WHERE status IN ('sent', 'replied') AND followup_at IS NOT NULL"
        ).fetchone()["n"]
    print(f"outreach_contacts: {outreach_contacts}")
    print(f"outreach_actions: {outreach_actions}")
    print(f"followups: {open_followups}")
    return 0


def connect() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    if SCHEMA.exists():
        with sqlite3.connect(DB) as bootstrap:
            bootstrap.executescript(SCHEMA.read_text())
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_add_application(args: argparse.Namespace) -> int:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO applications (company, role, url, source, status, applied_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.company,
                args.role,
                args.url,
                args.source,
                args.status,
                args.applied_at or datetime.now(timezone.utc).isoformat(),
                args.notes,
            ),
        )
        conn.commit()
    return 0


def cmd_list_applications(_: argparse.Namespace) -> int:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, company, role, status, applied_at, url FROM applications ORDER BY id DESC"
        ).fetchall()
    for row in rows:
        print(
            f"#{row['id']} {row['company']} — {row['role']} [{row['status']}] "
            f"{shorten(row['url'] or '', width=48, placeholder='...')}"
        )
    return 0


def cmd_brief(_: argparse.Namespace) -> int:
    if SCHEMA.exists():
        with sqlite3.connect(DB) as bootstrap:
            bootstrap.executescript(SCHEMA.read_text())
    with connect() as conn:
        rows = conn.execute(
            "SELECT company, role, status FROM applications ORDER BY id DESC LIMIT 5"
        ).fetchall()
    print("Daily brief")
    print("- Review 3 high-fit jobs")
    print("- Send 1 referral ask")
    print("- Tailor 1 application")
    print("- Update 1 story or proof point")
    if rows:
        print("Recent applications:")
        for row in rows:
            print(f"- {row['company']} — {row['role']} [{row['status']}]")
    return 0


def cmd_list_companies(_: argparse.Namespace) -> int:
    if not COMPANIES_FILE.exists():
        print("No target-company file yet. Run init.")
        return 1
    print(COMPANIES_FILE.read_text().strip())
    return 0


def cmd_add_contact(args: argparse.Namespace) -> int:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO outreach_contacts (person_name, title, company, connection_strength, source, last_touch, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (args.person_name, args.title, args.company, args.connection_strength, args.source, args.last_touch, args.notes),
        )
        conn.commit()
    return 0


def cmd_add_outreach(args: argparse.Namespace) -> int:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO outreach_actions
              (contact_id, company, role, channel, status, message_draft, artifact_ref, sent_at, followup_at, replied_at, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                args.contact_id,
                args.company,
                args.role,
                args.channel,
                args.status,
                args.message_draft,
                args.artifact_ref,
                args.sent_at,
                args.followup_at,
                args.replied_at,
                args.outcome,
            ),
        )
        conn.commit()
    return 0


def cmd_list_outreach(_: argparse.Namespace) -> int:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT a.id, a.company, a.role, a.channel, a.status, a.sent_at, a.followup_at, c.person_name
            FROM outreach_actions a
            LEFT JOIN outreach_contacts c ON c.id = a.contact_id
            ORDER BY a.id DESC
            """
        ).fetchall()
    if not rows:
        print("No outreach actions yet.")
        return 0
    for row in rows:
        who = row["person_name"] or "(no contact)"
        print(f"#{row['id']} {row['company']} — {row['role']} [{row['status']}] via {row['channel']} → {who}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="jobsearch-os")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("brief")
    sub.add_parser("list-applications")
    sub.add_parser("list-companies")
    sub.add_parser("list-outreach")

    add = sub.add_parser("add-application")
    add.add_argument("company")
    add.add_argument("role")
    add.add_argument("--url")
    add.add_argument("--source")
    add.add_argument("--status", default="new")
    add.add_argument("--applied-at")
    add.add_argument("--notes")

    contact = sub.add_parser("add-contact")
    contact.add_argument("person_name")
    contact.add_argument("company")
    contact.add_argument("--title")
    contact.add_argument("--connection-strength", type=int)
    contact.add_argument("--source")
    contact.add_argument("--last-touch")
    contact.add_argument("--notes")

    outreach = sub.add_parser("add-outreach")
    outreach.add_argument("company")
    outreach.add_argument("role")
    outreach.add_argument("--contact-id", type=int)
    outreach.add_argument("--channel", default="cold_email")
    outreach.add_argument("--status", default="draft")
    outreach.add_argument("--message-draft")
    outreach.add_argument("--artifact-ref")
    outreach.add_argument("--sent-at")
    outreach.add_argument("--followup-at")
    outreach.add_argument("--replied-at")
    outreach.add_argument("--outcome")

    args = parser.parse_args()
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "brief":
        return cmd_brief(args)
    if args.cmd == "list-applications":
        return cmd_list_applications(args)
    if args.cmd == "list-companies":
        return cmd_list_companies(args)
    if args.cmd == "list-outreach":
        return cmd_list_outreach(args)
    if args.cmd == "add-application":
        return cmd_add_application(args)
    if args.cmd == "add-contact":
        return cmd_add_contact(args)
    if args.cmd == "add-outreach":
        return cmd_add_outreach(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
