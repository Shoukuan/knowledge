#!/usr/bin/env python3
"""
Format Markdown files, insert per-file TOC, and generate a repository index up to N folder levels.

Usage:
    python scripts/format_and_index.py --root . --max-depth 5 --index docs/REPO_INDEX.md

Behavior:
- Normalize headings to ATX style (#)
- Ensure a single H1 title at top (from filename if missing)
- Insert or update TOC between <!-- TOC --> and <!-- TOC END --> based on headings H2-H4
- Generate repository index markdown linking files and folders up to given depth
"""
import argparse
import re
from pathlib import Path
from typing import List


def slugify(text: str) -> str:
    t = text.strip().lower()
    t = re.sub(r"[\s]+", "-", t)
    t = re.sub(r"[^a-z0-9\-_]", "", t)
    return t


def parse_headings(lines: List[str]):
    headings = []
    for i, ln in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            headings.append((i, level, text))
    return headings


def ensure_h1(lines: List[str], title: str) -> List[str]:
    # If first non-empty line is H1, keep. Else insert H1.
    for i, ln in enumerate(lines):
        if ln.strip() == '':
            continue
        if re.match(r'^#\s+.+', ln):
            return lines
        else:
            return ['# ' + title, '\n'] + lines
    return ['# ' + title, '\n']


def generate_toc(headings):
    toc_lines = ['<!-- TOC -->', '']
    for _, level, text in headings:
        if level == 1:
            continue
        if level > 4:
            continue
        indent = '  ' * (level - 2)
        anchor = slugify(text)
        toc_lines.append(f'{indent}- [{text}](#{anchor})')
    toc_lines.append('')
    toc_lines.append('<!-- TOC END -->')
    toc_lines.append('')
    return toc_lines


def update_file(path: Path):
    s = path.read_text(encoding='utf-8')
    # normalize line endings
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    lines = s.split('\n')

    # normalize headings: ensure single space after #
    for i, ln in enumerate(lines):
        m = re.match(r'^(#{1,6})\s*(.*)$', ln)
        if m:
            hashes = m.group(1)
            text = m.group(2).strip()
            lines[i] = f"{hashes} {text}"

    # Ensure H1
    title = path.stem.replace('_', ' ').replace('-', ' ').title()
    lines = ensure_h1(lines, title)

    # parse headings
    headings = parse_headings(lines)
    # build toc from headings
    toc = generate_toc(headings)

    # insert or replace TOC
    joined = '\n'.join(lines) + '\n'
    if '<!-- TOC -->' in joined and '<!-- TOC END -->' in joined:
        joined = re.sub(r'<!-- TOC -->.*?<!-- TOC END -->', '\n'.join(toc), joined, flags=re.S)
    else:
        # insert after H1
        joined = re.sub(r'^(#\s+.*?\n)', r"\1" + '\n'.join(toc) + '\n', joined, count=1, flags=re.M)

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
