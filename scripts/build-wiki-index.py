#!/usr/bin/env python3
"""
build-wiki-index.py — Build a SQLite FTS5 full-text search index over the Job Search OS wiki.

Usage:
  python3 scripts/build-wiki-index.py            # rebuild from workspace root
  python3 scripts/build-wiki-index.py --watch     # rebuild on file change (requires watchdog)

The index lives at data/wiki-index.db (gitignored).
Query it:
  SELECT path, title, snippet(wiki_fts, 2, '→', '←', '...', 15) as excerpt
  FROM wiki_fts WHERE wiki_fts MATCH 'pricing experimentation'
  ORDER BY rank LIMIT 5;
"""

import os, re, sqlite3, sys, argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
WIKI_DIRS = [
    WORKSPACE / "wiki",
    WORKSPACE.parent / "job-search-private" / "kb",
]
DB_PATH = WORKSPACE / "data" / "wiki-index.db"


def extract_title(content: str, path: Path) -> str:
    m = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    return m.group(1).strip() if m else path.stem.replace('-', ' ').title()


def extract_tags(content: str, path: Path) -> str:
    """Extract type tag from path + any frontmatter tags."""
    parts = path.parts
    for part in parts:
        if part in ('companies','evidence','resumes','outreach','profile',
                    'queue','interviews','jobs','roles','stories','reference'):
            return part
    return 'other'


def extract_sections(content: str) -> list[tuple[str, str]]:
    """Split content into (heading, body) pairs."""
    chunks = re.split(r'\n(#{1,3} .+)\n', content)
    if not chunks:
        return [('', content)]
    result = [('', chunks[0])]
    for i in range(1, len(chunks)-1, 2):
        result.append((chunks[i].lstrip('#').strip(), chunks[i+1]))
    return result


def strip_markdown(text: str) -> str:
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)   # wikilinks
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # md links
    text = re.sub(r'[#*`_~>|]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def build_index(verbose=True):
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS wiki_fts")
    conn.execute("""
        CREATE VIRTUAL TABLE wiki_fts USING fts5(
            path,
            title,
            section,
            type,
            content,
            tokenize='porter ascii'
        )
    """)
    conn.execute("DROP TABLE IF EXISTS wiki_meta")
    conn.execute("""
        CREATE TABLE wiki_meta (
            path TEXT PRIMARY KEY,
            title TEXT,
            type TEXT,
            related TEXT,
            indexed_at TEXT
        )
    """)

    count = 0
    for wiki_dir in WIKI_DIRS:
        if not wiki_dir.exists():
            continue
        for md_file in sorted(wiki_dir.rglob("*.md")):
            if any(x in str(md_file) for x in ['.gitkeep','sync-conflict',
                                                 'sources/','node_modules']):
                continue
            try:
                content = md_file.read_text(errors='replace')
                rel_path = str(md_file.relative_to(WORKSPACE.parent))
                title = extract_title(content, md_file)
                ftype = extract_tags(content, md_file)
                # extract Related links
                related_m = re.search(r'## Related\n([\s\S]+?)(?:\n##|\Z)', content)
                related = related_m.group(1).strip() if related_m else ''

                # index per section for precise snippets
                sections = extract_sections(content)
                for heading, body in sections:
                    clean = strip_markdown(body)
                    if len(clean) < 10:
                        continue
                    conn.execute(
                        "INSERT INTO wiki_fts(path, title, section, type, content) VALUES (?,?,?,?,?)",
                        (rel_path, title, heading, ftype, clean)
                    )

                conn.execute(
                    "INSERT OR REPLACE INTO wiki_meta VALUES (?,?,?,?,?)",
                    (rel_path, title, ftype, related, datetime.utcnow().isoformat())
                )
                count += 1
            except Exception as e:
                print(f"  WARN {md_file}: {e}", file=sys.stderr)

    conn.commit()
    conn.close()
    if verbose:
        print(f"[wiki-index] Indexed {count} pages → {DB_PATH}")
    return count


def search(query: str, limit: int = 8) -> list[dict]:
    """Helper: search the index and return ranked results."""
    if not DB_PATH.exists():
        build_index(verbose=False)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT DISTINCT path, title, type,
               snippet(wiki_fts, 4, '→', '←', '...', 20) as excerpt,
               rank
        FROM wiki_fts
        WHERE wiki_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit)).fetchall()
    conn.close()
    return [{'path': r[0], 'title': r[1], 'type': r[2],
             'excerpt': r[3], 'score': r[4]} for r in rows]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build Job Search OS wiki FTS index')
    parser.add_argument('--search', '-s', help='Test search query after build')
    parser.add_argument('--quiet', '-q', action='store_true')
    args = parser.parse_args()
    build_index(verbose=not args.quiet)
    if args.search:
        results = search(args.search)
        print(f"\nSearch: '{args.search}' → {len(results)} results")
        for r in results:
            print(f"  [{r['type']}] {r['title']} ({r['path']})")
            print(f"    {r['excerpt']}\n")
