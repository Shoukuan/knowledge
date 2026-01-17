#!/usr/bin/env python3
"""
查找仓库中超过指定大小的文件并导出清单。

用法:
    python scripts/find_large_files.py --path . --threshold 1 --out large_files.csv

默认阈值为 1MB。脚本会跳过 `.git` 目录并生成 CSV/Markdown 报告。
"""
import os
import argparse
import csv
from pathlib import Path


def human_size(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.2f}{unit}"
        n /= 1024.0
    return f"{n:.2f}PB"


def find_large_files(root: Path, threshold_bytes: int):
    results = []
    total_scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # skip .git
        if '.git' in dirpath.split(os.sep):
            continue
        for fn in filenames:
            total_scanned += 1
            fp = Path(dirpath) / fn
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size >= threshold_bytes:
                try:
                    rel = str(fp.relative_to(root))
                except Exception:
                    rel = str(fp)
                results.append((rel, size))
    return results, total_scanned


def write_csv(out_path: Path, rows):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['path','size_bytes','size_human'])
        for p,s in rows:
            writer.writerow([p, s, human_size(s)])


def write_md(out_path: Path, rows):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        f.write('# Large files report\n\n')
        f.write('| Path | Size |\n')
        f.write('|---|---:|\n')
        for p,s in rows:
            f.write(f'| {p} | {human_size(s)} |\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--path', '-p', default='.', help='仓库根目录或要扫描的目录')
    p.add_argument('--threshold', '-t', type=float, default=1.0, help='阈值，单位 MB（默认 1）')
    p.add_argument('--out', '-o', default='large_files.csv', help='CSV 输出文件路径')
    p.add_argument('--md', action='store_true', help='同时生成 Markdown 报告')
    args = p.parse_args()

    root = Path(args.path).resolve()
    threshold_bytes = int(args.threshold * 1024 * 1024)

    rows, scanned = find_large_files(root, threshold_bytes)
    rows.sort(key=lambda x: x[1], reverse=True)

    out_csv = Path(args.out)
    write_csv(out_csv, rows)
    if args.md:
        write_md(out_csv.with_suffix('.md'), rows)

    total_size = sum(s for _,s in rows)
    print(f"Scanned files: {scanned}")
    print(f"Found {len(rows)} files >= {args.threshold} MB, total: {human_size(total_size)}")
    print(f"CSV written to: {out_csv}")
    if args.md:
        print(f"MD written to: {out_csv.with_suffix('.md')}")


if __name__ == '__main__':
    main()
