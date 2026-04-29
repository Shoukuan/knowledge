#!/usr/bin/env python3
"""
Promote audited source-stub markdown files by filling structured source metadata.

Usage:
    python scripts/promote_source_stubs.py --root .
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from frontmatter_utils import dump_frontmatter, ensure_h1, split_frontmatter, title_from_body


TODAY = date.today().isoformat()


def merge_unique(existing, incoming):
    items = list(existing) if isinstance(existing, list) else []
    for value in incoming:
        if value not in items:
            items.append(value)
    return items


def promote_file(path: Path, entry: dict) -> bool:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    title = str(meta.get("title", "")).strip() or title_from_body(body, path)

    meta["title"] = title
    meta["type"] = "source"
    meta["status"] = "active"
    meta["sources"] = merge_unique(meta.get("sources", []), entry.get("sample_urls", []))
    meta["updated_at"] = TODAY

    rendered = dump_frontmatter(meta) + "\n" + ensure_h1(body, title).strip("\n") + "\n"
    if rendered == raw:
        return False
    path.write_text(rendered, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--audit-json", default="reports/external_links_audit.json", help="audit json path")
    parser.add_argument("--limit", type=int, default=20, help="max files to promote")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entries = json.loads((root / args.audit_json).read_text(encoding="utf-8"))
    candidates = [
        entry
        for entry in entries
        if entry["category"] == "source_stub"
        and not entry["path"].startswith("wiki/sources/")
        and entry["missing_frontmatter_sources"]
    ]
    candidates.sort(key=lambda item: (-item["external_url_count"], item["path"]))

    changed = 0
    touched: list[str] = []
    for entry in candidates[: args.limit]:
        path = root / entry["path"]
        if promote_file(path, entry):
            changed += 1
            touched.append(entry["path"])

    print(f"Promoted {changed} source-stub files")
    for item in touched:
        print(item)


if __name__ == "__main__":
    main()
