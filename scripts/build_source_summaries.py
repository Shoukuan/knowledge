#!/usr/bin/env python3
"""
Build source summary pages for internal markdown sources referenced by wiki pages.

Usage:
    python scripts/build_source_summaries.py --root .
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from posixpath import relpath

from frontmatter_utils import dump_frontmatter, split_frontmatter, strip_markup_for_snippet


TODAY = date.today().isoformat()
HEADING_RE = re.compile(r"^(##+)\s+(.+)$", re.M)


def repo_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def first_h1(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def collect_internal_sources(root: Path) -> tuple[list[str], dict[str, list[str]], dict[str, str]]:
    source_notes: set[str] = set()
    related_pages: dict[str, list[str]] = {}
    wiki_titles: dict[str, str] = {}

    for wiki_path in sorted((root / "wiki").rglob("*.md")):
        rel = repo_rel(root, wiki_path)
        meta, body = split_frontmatter(wiki_path.read_text(encoding="utf-8"))
        wiki_titles[rel] = str(meta.get("title", "")).strip() or first_h1(body, wiki_path.stem)
        for src in meta.get("sources", []):
            if isinstance(src, str) and src.endswith(".md") and not src.startswith("wiki/"):
                source_notes.add(src)
                related_pages.setdefault(src, [])
                if rel not in related_pages[src]:
                    related_pages[src].append(rel)

    return sorted(source_notes), related_pages, wiki_titles


def summary_path(root: Path, source_rel: str) -> Path:
    return root / "wiki" / "sources" / Path(source_rel)


def md_link(from_path: Path, target: str, label: str | None = None) -> str:
    target_path = Path(target).as_posix()
    source_dir = from_path.parent.as_posix()
    rel = relpath(target_path, source_dir or ".")
    return f"[{label or Path(target).stem}]({rel})"


def wikilink_label(title: str) -> str:
    return title


def external_sources(meta_sources: object) -> list[str]:
    items = meta_sources if isinstance(meta_sources, list) else []
    return [item for item in items if isinstance(item, str) and item.startswith("http")]


def heading_outline(body: str, limit: int = 8) -> list[str]:
    results: list[str] = []
    for match in HEADING_RE.finditer(body):
        level = len(match.group(1))
        text = match.group(2).strip()
        if not text:
            continue
        indent = "  " * max(0, level - 2)
        results.append(f"{indent}- {text}")
        if len(results) >= limit:
            break
    return results


def render_source_page(
    page_path: Path,
    source_rel: str,
    source_meta: dict,
    source_body: str,
    related: list[str],
    wiki_titles: dict[str, str],
) -> str:
    note_title = str(source_meta.get("title", "")).strip() or first_h1(source_body, Path(source_rel).stem)
    page_title = f"{note_title}（资料摘要）"
    tags = ["source"]
    for tag in source_meta.get("tags", []):
        if tag not in tags:
            tags.append(tag)

    meta = {
        "title": page_title,
        "type": "source",
        "status": "active",
        "tags": tags,
        "aliases": [note_title],
        "sources": [source_rel],
        "updated_at": TODAY,
    }

    snippet = strip_markup_for_snippet(source_body) or "该资料当前已被纳入知识库，但仍需要进一步补充更细粒度摘要。"
    headings = heading_outline(source_body)
    ext_refs = external_sources(source_meta.get("sources", []))

    lines = [
        dump_frontmatter(meta),
        f"# {page_title}",
        "",
        f"这是对 `{source_rel}` 的追溯页，用来连接原始笔记与当前知识地图。",
        "",
        "## 原始位置",
        "",
        f"- {md_link(page_path, source_rel, note_title)}",
        "",
        "## 摘要",
        "",
        snippet,
        "",
    ]

    if headings:
        lines.extend(["## 结构线索", ""])
        lines.extend(headings)
        lines.append("")

    if related:
        lines.extend(["## 关联 Wiki 页面", ""])
        for rel in related:
            title = wiki_titles.get(rel, Path(rel).stem)
            lines.append(f"- [[{wikilink_label(title)}]]")
        lines.append("")

        lines.extend(["## 可点击导航", ""])
        for rel in related:
            title = wiki_titles.get(rel, Path(rel).stem)
            lines.append(f"- {md_link(page_path, rel, title)}")
        lines.append("")

    if ext_refs:
        lines.extend(["## 外部参考", ""])
        for ref in ext_refs:
            lines.append(f"- {ref}")
        lines.append("")

    return "\n".join(lines)


def render_sources_index(root: Path, source_pages: list[str]) -> str:
    meta = {
        "title": "Source Index",
        "type": "index",
        "status": "active",
        "tags": ["wiki", "sources", "index"],
        "aliases": ["资料索引", "Source Summaries"],
        "sources": [],
        "updated_at": TODAY,
    }
    groups: dict[str, list[str]] = {}
    for rel in source_pages:
        parts = Path(rel).parts
        group = parts[2] if len(parts) >= 3 else "misc"
        groups.setdefault(group, []).append(rel)

    lines = [
        dump_frontmatter(meta),
        "# Source Index",
        "",
        "这里汇总 `wiki/sources/` 下的资料摘要页，用来追溯 wiki 页面背后的原始笔记。",
        "",
    ]

    for group in sorted(groups):
        lines.extend([f"## {group}", ""])
        for rel in sorted(groups[group]):
            page = root / rel
            meta_page, body = split_frontmatter(page.read_text(encoding="utf-8"))
            title = str(meta_page.get("title", "")).strip() or first_h1(body, page.stem)
            link = relpath(rel, "wiki/sources")
            lines.append(f"- [{title}]({link})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source_notes, related_pages, wiki_titles = collect_internal_sources(root)
    written = 0
    source_page_rels: list[str] = []

    for source_rel in source_notes:
        source_path = root / source_rel
        if not source_path.exists():
            continue
        page_path = summary_path(root, source_rel)
        page_path.parent.mkdir(parents=True, exist_ok=True)
        source_meta, source_body = split_frontmatter(source_path.read_text(encoding="utf-8"))
        rendered = render_source_page(page_path, source_rel, source_meta, source_body, related_pages.get(source_rel, []), wiki_titles)
        if not rendered.endswith("\n"):
            rendered += "\n"
        page_path.write_text(rendered, encoding="utf-8")
        source_page_rels.append(repo_rel(root, page_path))
        written += 1

    index_path = root / "wiki" / "sources" / "index.md"
    index_rendered = render_sources_index(root, source_page_rels)
    if not index_rendered.endswith("\n"):
        index_rendered += "\n"
    index_path.write_text(index_rendered, encoding="utf-8")

    print(f"Generated {written} source summary pages and source index")


if __name__ == "__main__":
    main()
