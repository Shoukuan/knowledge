#!/usr/bin/env python3
"""
Add or repair first-version frontmatter across Markdown files.

Usage:
    python scripts/normalize_frontmatter.py --root .
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Dict

from frontmatter_utils import dump_frontmatter, ensure_h1, split_frontmatter, tags_from_path, title_from_body


TODAY = date.today().isoformat()


def infer_type(rel: Path) -> str:
    path = rel.as_posix()
    if path == "README.md":
        return "hub"
    if path == "purpose.md":
        return "purpose"
    if path == "schema.md":
        return "schema"
    if path == "wiki/index.md":
        return "index"
    if path == "wiki/overview.md":
        return "overview"
    if path == "wiki/log.md":
        return "log"
    if path.startswith("wiki/entities/"):
        return "entity"
    if path.startswith("wiki/concepts/"):
        return "concept"
    if path.startswith("wiki/sources/"):
        return "source"
    if path.startswith("wiki/queries/"):
        return "query"
    if path.startswith("docs/"):
        return "reference"
    if path.startswith("scripts/"):
        return "guide"
    return "note"


def infer_status(page_type: str) -> str:
    if page_type in {"hub", "purpose", "schema", "index", "overview", "log"}:
        return "active"
    if page_type in {"reference", "guide"}:
        return "active"
    return "seed"


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if rel == "docs/REPO_INDEX.md":
        return True
    return any(part.startswith(".") for part in path.parts)


def normalize_meta(path: Path, meta: Dict[str, object], body: str, root: Path) -> Dict[str, object]:
    rel = path.relative_to(root)
    title = str(meta.get("title", "")).strip() or title_from_body(body, path)
    page_type = str(meta.get("type", "")).strip() or infer_type(rel)
    tags = meta.get("tags")
    aliases = meta.get("aliases")
    sources = meta.get("sources")

    if not isinstance(tags, list):
        tags = tags_from_path(rel)
    if not isinstance(aliases, list):
        aliases = []
    if not isinstance(sources, list):
        sources = []

    normalized = {
        "title": title,
        "type": page_type,
        "status": str(meta.get("status", "")).strip() or infer_status(page_type),
        "tags": tags,
        "aliases": aliases,
        "sources": sources,
        "updated_at": str(meta.get("updated_at", "")).strip() or TODAY,
    }
    return normalized


def normalize_file(path: Path, root: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    normalized_meta = normalize_meta(path, meta, body, root)
    normalized_body = ensure_h1(body, str(normalized_meta["title"]))
    rendered = dump_frontmatter(normalized_meta) + "\n" + normalized_body.strip("\n") + "\n"

    if rendered == raw.replace("\r\n", "\n").replace("\r", "\n"):
        return False
    path.write_text(rendered, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changed = 0
    scanned = 0
    for path in sorted(root.rglob("*.md")):
        if should_skip(path, root):
            continue
        scanned += 1
        if normalize_file(path, root):
            changed += 1

    print(f"Normalized frontmatter for {changed}/{scanned} markdown files")


if __name__ == "__main__":
    main()
