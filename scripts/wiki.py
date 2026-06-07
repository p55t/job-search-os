from __future__ import annotations

"""Deterministic wiki utilities for Job Search OS.

Commands:
  python3 scripts/wiki.py index   # regenerate wiki/INDEX.md and wiki/aliases.md
  python3 scripts/wiki.py lint    # report broken wiki links and orphans

The script is intentionally stdlib-only so it can run in cron and in fresh
checkouts without extra dependencies.
"""

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
INDEX_FILE = WIKI / "INDEX.md"
ALIASES_FILE = WIKI / "aliases.md"
EXCLUDE = {INDEX_FILE, ALIASES_FILE}

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]")
HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Page:
    path: Path
    rel: str
    title: str
    summary: str
    aliases: tuple[str, ...]
    section: str


def strip_frontmatter(text: str) -> tuple[str, dict[str, list[str]]]:
    meta: dict[str, list[str]] = {}
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text, meta
    body = text[m.end():]
    fm = m.group(1)
    current_key: str | None = None
    for raw in fm.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*", line):
            key, rest = line.split(":", 1)
            key = key.strip()
            value = rest.strip()
            current_key = key
            if value.startswith("[") and value.endswith("]"):
                items = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
                meta[key] = items
            elif value:
                meta[key] = [value.strip('"\'')]
            else:
                meta.setdefault(key, [])
        elif current_key and line.lstrip().startswith("-"):
            meta.setdefault(current_key, []).append(line.lstrip()[1:].strip().strip('"\''))
    return body, meta


def title_for(text: str, path: Path) -> str:
    match = HEADING_RE.search(text)
    if match:
        return match.group(1).strip()
    return path.stem.replace("-", " ").title()


def summary_for(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    start = 0
    while start < len(lines) and not lines[start]:
        start += 1
    while start < len(lines) and lines[start].startswith("#"):
        start += 1
    while start < len(lines) and not lines[start]:
        start += 1
    para: list[str] = []
    for line in lines[start:]:
        if not line:
            if para:
                break
            continue
        if line.startswith("#") and para:
            break
        if line.startswith("#"):
            continue
        if line.startswith("-") and not para:
            para.append(line.lstrip("- "))
        elif line:
            para.append(line)
    summary = " ".join(para).strip()
    summary = re.sub(r"\s+", " ", summary)
    return summary[:140].rstrip()


def normalize_alias(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def page_section(rel: str) -> str:
    return rel.split("/", 1)[0] if "/" in rel else "root"


def scan_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted(WIKI.rglob("*.md")):
        if path in EXCLUDE:
            continue
        rel = path.relative_to(WIKI).with_suffix("").as_posix()
        text = path.read_text(errors="replace")
        body, meta = strip_frontmatter(text)
        title = meta.get("title", [title_for(body, path)])[0]
        summary = summary_for(body)
        aliases = tuple(dict.fromkeys(
            [path.stem.replace("-", " ").title(), rel.replace("/", " ")] + meta.get("aliases", [])
        ))
        pages.append(Page(path=path, rel=rel, title=title, summary=summary, aliases=aliases, section=page_section(rel)))
    return pages


def render_index(pages: list[Page]) -> str:
    sections: dict[str, list[Page]] = defaultdict(list)
    for page in pages:
        sections[page.section].append(page)
    lines = [
        "# Wiki Index",
        "",
        "> Content catalog for Job Search OS.",
        "> Read this first to find the right page for a query or update.",
        f"> Total pages: {len(pages)}",
        "",
    ]
    for section in sorted(sections):
        lines.append(f"## {section.title()}")
        for page in sorted(sections[section], key=lambda p: p.title.lower()):
            link = f"[[{page.rel}|{page.title}]]"
            summary = page.summary or "No summary yet."
            lines.append(f"- {link} — {summary}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_aliases(pages: list[Page]) -> str:
    alias_map = build_alias_map(pages)
    alias_rows = sorted(alias_map.items())
    lines = [
        "# Aliases",
        "",
        "> Generated alias map for Job Search OS.",
        f"> Total aliases: {len(alias_rows)}",
        "",
        "| Alias | Page |",
        "|---|---|",
    ]
    for alias, rel in alias_rows:
        lines.append(f"| `{alias}` | `[[{rel}]]` |")
    lines.append("")
    return "\n".join(lines)


def build_alias_map(pages: list[Page]) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    collisions: dict[str, set[str]] = defaultdict(set)
    for page in pages:
        for alias in page.aliases:
            norm = normalize_alias(alias)
            if not norm:
                continue
            if norm in alias_map and alias_map[norm] != page.rel:
                collisions[norm].update({alias_map[norm], page.rel})
                continue
            alias_map[norm] = page.rel
    if collisions:
        print("ALIAS COLLISIONS")
        for alias, rels in sorted(collisions.items()):
            print(f"- {alias}: {', '.join(sorted(rels))}")
    return alias_map


def find_links(text: str) -> Iterable[str]:
    for match in LINK_RE.finditer(text):
        yield match.group(1).strip()


def resolve_link(link: str, pages: dict[str, Page], alias_map: dict[str, str]) -> str | None:
    candidate = link.split("#", 1)[0].strip()
    candidate = candidate.rstrip("/")
    if candidate.endswith(".md"):
        candidate = candidate[:-3]
    candidate = candidate.lstrip("./")
    if candidate in pages:
        return candidate
    norm = normalize_alias(candidate.replace("/", " "))
    return alias_map.get(norm)


def lint(pages: list[Page], strict_orphans: bool = False) -> int:
    page_map = {page.rel: page for page in pages}
    alias_map = build_alias_map(pages)
    inbound: dict[str, set[str]] = {page.rel: set() for page in pages}
    broken: list[tuple[str, str]] = []

    for page in pages:
        text = page.path.read_text(errors="replace")
        _, meta = strip_frontmatter(text)
        for link in find_links(text):
            target = resolve_link(link, page_map, alias_map)
            if target is None:
                broken.append((page.rel, link))
            else:
                inbound[target].add(page.rel)

    orphans = [rel for rel, refs in inbound.items() if not refs and rel not in {"profile/me", "profile/positioning"}]

    if broken:
        print("BROKEN LINKS")
        for src, link in broken:
            print(f"- {src} -> [[{link}]]")
    if orphans:
        print("ORPHANS")
        for rel in sorted(orphans):
            print(f"- {rel}")

    if broken or (strict_orphans and orphans):
        return 1
    return 0


def cmd_index(_: argparse.Namespace) -> int:
    pages = scan_pages()
    INDEX_FILE.write_text(render_index(pages))
    ALIASES_FILE.write_text(render_aliases(pages))
    print(f"wrote {INDEX_FILE.relative_to(ROOT)}")
    print(f"wrote {ALIASES_FILE.relative_to(ROOT)}")
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    pages = scan_pages()
    return lint(pages, strict_orphans=args.strict_orphans)


def main() -> int:
    parser = argparse.ArgumentParser(description="Job Search OS wiki utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="Generate wiki/INDEX.md and wiki/aliases.md")
    lint_parser = sub.add_parser("lint", help="Check for broken links and orphans")
    lint_parser.add_argument("--strict-orphans", action="store_true", help="Treat orphan pages as a failure")

    args = parser.parse_args()
    if args.cmd == "index":
        return cmd_index(args)
    if args.cmd == "lint":
        return cmd_lint(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
