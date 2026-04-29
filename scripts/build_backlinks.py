#!/usr/bin/env python3
"""
Generate backlinks sections for wiki pages based on wikilinks and markdown links.

Usage:
    python scripts/build_backlinks.py --root .
"""

from __future__ import annotations

import argparse
from pathlib import Path
from posixpath import normpath, relpath
import re

from frontmatter_utils import dump_frontmatter, parse_markdown_links, parse_wikilinks, split_frontmatter


BACKLINKS_HEADER = "## 反向链接"
START = "<!-- BACKLINKS START -->"
END = "<!-- BACKLINKS END -->"
BACKLINKS_BLOCK_RE = re.compile(
    rf"\n*{re.escape(BACKLINKS_HEADER)}\n\n{re.escape(START)}.*?{re.escape(END)}\n*",
    re.S,
)


def repo_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def first_h1(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_title_maps(root: Path, wiki_files: list[Path]) -> tuple[dict[str, str], dict[str, str]]:
    title_to_path: dict[str, str] = {}
    path_to_title: dict[str, str] = {}
    for path in wiki_files:
        rel = repo_rel(root, path)
        _, body = split_frontmatter(path.read_text(encoding="utf-8"))
        title = first_h1(body, path.stem)
        path_to_title[rel] = title
        title_to_path[title] = rel
        title_to_path[path.stem] = rel
    return title_to_path, path_to_title


def resolve_target(source_rel: str, target: str, title_to_path: dict[str, str]) -> str | None:
    target = target.strip()
    if target in title_to_path:
        return title_to_path[target]

    if target.startswith("wiki/") and target in title_to_path.values():
        return target

    if target.endswith(".md"):
        source_dir = Path(source_rel).parent.as_posix()
        candidate = normpath(f"{source_dir}/{target}")
        if candidate in title_to_path.values():
            return candidate

    return None


def remove_existing_backlinks(body: str) -> str:
    cleaned = BACKLINKS_BLOCK_RE.sub("\n", body).rstrip()
    return cleaned + "\n"


def render_backlinks_section(page_rel: str, refs: list[str], path_to_title: dict[str, str]) -> str:
    lines = [BACKLINKS_HEADER, "", START]
    if refs:
        source_dir = Path(page_rel).parent.as_posix()
        for ref in refs:
            title = path_to_title.get(ref, Path(ref).stem)
            target = relpath(ref, source_dir or ".")
            lines.append(f"- [{title}]({target})")
    else:
        lines.append("- 暂无反向链接")
    lines.append(END)
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    wiki_files = sorted((root / "wiki").rglob("*.md"))
    title_to_path, path_to_title = build_title_maps(root, wiki_files)
    backlinks: dict[str, set[str]] = {repo_rel(root, path): set() for path in wiki_files}

    for path in wiki_files:
        rel = repo_rel(root, path)
        _, body = split_frontmatter(path.read_text(encoding="utf-8"))
        targets: set[str] = set()

        for target in parse_wikilinks(body):
            resolved = resolve_target(rel, target, title_to_path)
            if resolved and resolved != rel:
                targets.add(resolved)

        for _, target in parse_markdown_links(body):
            if target.startswith("http"):
                continue
            resolved = resolve_target(rel, target, title_to_path)
            if resolved and resolved != rel:
                targets.add(resolved)

        for target in targets:
            backlinks.setdefault(target, set()).add(rel)

    changed = 0
    for path in wiki_files:
        rel = repo_rel(root, path)
        raw = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        body = remove_existing_backlinks(body)
        section = render_backlinks_section(rel, sorted(backlinks.get(rel, set())), path_to_title)
        rendered = dump_frontmatter(meta) + "\n" + body.rstrip() + "\n\n" + section
        if not rendered.endswith("\n"):
            rendered += "\n"
        if rendered != raw:
            path.write_text(rendered, encoding="utf-8")
            changed += 1

    print(f"Updated backlinks for {changed} wiki pages")


if __name__ == "__main__":
    main()
