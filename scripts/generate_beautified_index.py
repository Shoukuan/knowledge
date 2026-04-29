#!/usr/bin/env python3
"""
Generate a frontmatter-aware repository index and search index.

Usage:
  python scripts/generate_beautified_index.py --root . --out docs/REPO_INDEX.md --search docs/search_index.json
"""
import argparse
import json
from pathlib import Path

from frontmatter_utils import split_frontmatter, strip_markup_for_snippet, title_from_body


def title_from_md(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return path.stem
    meta, body = split_frontmatter(s)
    title = str(meta.get('title', '')).strip()
    if title:
        return title
    return title_from_body(body, path)


def snippet_from_md(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return ''
    _, body = split_frontmatter(s)
    return strip_markup_for_snippet(body)


def metadata_from_md(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return {}
    meta, _ = split_frontmatter(s)
    return meta


def should_skip(path: Path, out_md: Path, search_json: Path) -> bool:
    resolved = path.resolve()
    return resolved in {out_md.resolve(), search_json.resolve()}


def format_meta_suffix(meta: dict) -> str:
    parts = []
    page_type = str(meta.get('type', '')).strip()
    tags = meta.get('tags', [])
    if page_type:
        parts.append(f'type: `{page_type}`')
    if isinstance(tags, list) and tags:
        parts.append('tags: ' + ', '.join(str(tag) for tag in tags[:4]))
    if not parts:
        return ''
    return ' · ' + ' · '.join(parts)


def build_index(root: Path, out_md: Path, search_json: Path, max_depth=5):
    root = root.resolve()
    entries = sorted([p for p in root.iterdir() if not p.name.startswith('.')], key=lambda x: (not x.is_dir(), x.name.lower()))

    md_lines = ['# 仓库索引（美化版）', '', '使用搜索页面: [搜索库文档](search.html)', '', '']

    search_entries = []

    def walk_dir(p: Path, depth: int):
        if depth > max_depth:
            return []
        items = sorted([q for q in p.iterdir() if not q.name.startswith('.')], key=lambda x: (not x.is_dir(), x.name.lower()))
        lines = []
        for it in items:
            rel = it.relative_to(root).as_posix()
            if should_skip(it, out_md, search_json):
                continue
            if it.is_dir():
                # details block per directory
                lines.append('<details>')
                lines.append(f'  <summary>📁 {it.name}/</summary>')
                sub_lines = walk_dir(it, depth+1)
                for sl in sub_lines:
                    lines.append('  ' + sl)
                lines.append('</details>')
            else:
                display = it.name
                meta = metadata_from_md(it) if it.suffix.lower() == '.md' else {}
                lines.append(f'- [{display}]({rel}){format_meta_suffix(meta)}')
                if it.suffix.lower() == '.md':
                    title = title_from_md(it)
                    snippet = snippet_from_md(it)
                    search_entries.append({
                        'title': title,
                        'path': rel,
                        'snippet': snippet,
                        'type': meta.get('type', ''),
                        'tags': meta.get('tags', []),
                        'aliases': meta.get('aliases', []),
                    })
        return lines

    for e in entries:
        if should_skip(e, out_md, search_json):
            continue
        if e.is_dir():
            md_lines.append(f'## {e.name}')
            md_lines.append('')
            md_lines.extend(walk_dir(e, 1))
            md_lines.append('')
        else:
            rel = e.relative_to(root).as_posix()
            meta = metadata_from_md(e) if e.suffix.lower() == '.md' else {}
            md_lines.append(f'- [{e.name}]({rel}){format_meta_suffix(meta)}')
            if e.suffix.lower() == '.md':
                title = title_from_md(e)
                snippet = snippet_from_md(e)
                search_entries.append({
                    'title': title,
                    'path': rel,
                    'snippet': snippet,
                    'type': meta.get('type', ''),
                    'tags': meta.get('tags', []),
                    'aliases': meta.get('aliases', []),
                })

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text('\n'.join(md_lines) + '\n', encoding='utf-8')

    search_json.parent.mkdir(parents=True, exist_ok=True)
    search_json.write_text(json.dumps(search_entries, ensure_ascii=False, indent=2), encoding='utf-8')

    return len(search_entries)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='repo root')
    p.add_argument('--out', default='docs/REPO_INDEX.md', help='output md path')
    p.add_argument('--search', default='docs/search_index.json', help='output search json')
    p.add_argument('--max-depth', type=int, default=5)
    args = p.parse_args()

    root = Path(args.root)
    out = Path(args.out)
    search = Path(args.search)
    count = build_index(root, out, search, args.max_depth)
    print(f'Wrote {out} and search index ({count} entries) to {search}')


if __name__ == '__main__':
    main()
