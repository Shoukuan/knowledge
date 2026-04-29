#!/usr/bin/env python3
"""
Normalize Markdown headings and generate a repository index up to N folder levels.

Usage:
    python scripts/format_and_index.py --root . --max-depth 5 --index docs/REPO_INDEX.md

Behavior:
- Normalize headings to ATX style (#)
- Ensure a single H1 title at top (from filename if missing)
- Generate repository index markdown linking files and folders up to given depth
"""
import argparse
import re
from pathlib import Path

from frontmatter_utils import dump_frontmatter, ensure_h1, split_frontmatter, title_from_body


def update_file(path: Path):
    s = path.read_text(encoding='utf-8')
    meta, body = split_frontmatter(s)
    lines = body.split('\n')

    # normalize headings: ensure single space after #
    for i, ln in enumerate(lines):
        m = re.match(r'^(#{1,6})\s*(.*)$', ln)
        if m:
            hashes = m.group(1)
            text = m.group(2).strip()
            lines[i] = f"{hashes} {text}"

    # Ensure H1
    joined = '\n'.join(lines)
    title = str(meta.get('title', '')).strip() or title_from_body(joined, path)
    joined = ensure_h1(joined, title)
    if meta:
        joined = dump_frontmatter(meta) + '\n' + joined

    # ensure trailing newline
    if not joined.endswith('\n'):
        joined += '\n'
    path.write_text(joined, encoding='utf-8')


def build_index(root: Path, out: Path, max_depth: int):
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ['# 仓库目录索引', '']
    def walk(dirpath: Path, depth: int):
        if depth > max_depth:
            return
        entries = sorted([p for p in dirpath.iterdir() if not p.name.startswith('.')], key=lambda x: (x.is_file(), x.name.lower()))
        for p in entries:
            rel = p.relative_to(root).as_posix()
            indent = '  ' * (depth - 1)
            if p.is_dir():
                lines.append(f'{indent}- **{p.name}/**')
                walk(p, depth+1)
            else:
                display = p.name
                lines.append(f'{indent}- [{display}]({rel})')

    walk(root, 1)
    out.write_text('\n'.join(lines)+"\n", encoding='utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.', help='repo root')
    p.add_argument('--max-depth', type=int, default=5, help='max directory depth for index')
    p.add_argument('--index', default='docs/REPO_INDEX.md', help='output index file')
    args = p.parse_args()

    root = Path(args.root).resolve()
    md_files = list(root.rglob('*.md'))
    # skip files in .git and docs generated file
    md_files = [p for p in md_files if '.git' not in p.parts and p.resolve() != (root / args.index).resolve()]

    for p in md_files:
        try:
            update_file(p)
        except Exception as e:
            print(f'Failed to update {p}: {e}')

    build_index(root, root / args.index, args.max_depth)
    print(f'Updated {len(md_files)} markdown files and wrote index to {args.index}')


if __name__ == '__main__':
    main()
