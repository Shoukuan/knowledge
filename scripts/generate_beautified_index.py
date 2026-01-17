#!/usr/bin/env python3
"""
Generate a beautified REPO_INDEX.md with collapsible sections by top-level folder
and produce a search index JSON for a simple client-side search page.

Usage:
  python scripts/generate_beautified_index.py --root . --out docs/REPO_INDEX.md --search docs/search_index.json
"""
import argparse
import json
from pathlib import Path
import re


def title_from_md(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return path.stem
    m = re.search(r'^#\s+(.+)', s, flags=re.M)
    if m:
        return m.group(1).strip()
    # fallback first non-empty line
    for ln in s.splitlines():
        if ln.strip():
            return ln.strip()[:80]
    return path.stem


def snippet_from_md(path: Path):
    try:
        s = path.read_text(encoding='utf-8')
    except Exception:
        return ''
    # remove headings and code blocks then take first paragraph
    s = re.sub(r'```.*?```', '', s, flags=re.S)
    s = re.sub(r'^#+.*$', '', s, flags=re.M)
    for p in s.split('\n\n'):
        t = p.strip()
        if t:
            return t.replace('\n',' ')[:240]
    return ''


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
                lines.append(f'- [{display}]({rel})')
                if it.suffix.lower() == '.md':
                    title = title_from_md(it)
                    snippet = snippet_from_md(it)
                    search_entries.append({'title': title, 'path': rel, 'snippet': snippet})
        return lines

    for e in entries:
        if e.is_dir():
            md_lines.append(f'## {e.name}')
            md_lines.append('')
            md_lines.extend(walk_dir(e, 1))
            md_lines.append('')
        else:
            rel = e.relative_to(root).as_posix()
            md_lines.append(f'- [{e.name}]({rel})')
            if e.suffix.lower() == '.md':
                title = title_from_md(e)
                snippet = snippet_from_md(e)
                search_entries.append({'title': title, 'path': rel, 'snippet': snippet})

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
