#!/usr/bin/env python3
"""
Audit external links in Markdown files and produce an actionable report.

Usage:
    python scripts/audit_external_links.py --root .
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from frontmatter_utils import parse_markdown_links, split_frontmatter, strip_markup_for_snippet


URL_RE = re.compile(r"https?://[^\s<>)\"']+")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.I)
HTML_SRC_RE = re.compile(r'src=["\'](https?://[^"\']+)["\']', re.I)
HEADING_RE = re.compile(r"^#+\s+", re.M)
WHITESPACE_RE = re.compile(r"\s+")


def repo_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def first_h1(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def normalize_url(url: str) -> str:
    return url.rstrip(".,);]>")


def collect_external_urls(text: str) -> dict[str, list[str]]:
    markdown_links: list[str] = []
    image_links: list[str] = []
    html_links: list[str] = []
    naked_links: list[str] = []

    for _, target in MARKDOWN_LINK_RE.findall(text):
        if target.startswith("http://") or target.startswith("https://"):
            markdown_links.append(normalize_url(target))

    for _, target in MARKDOWN_IMAGE_RE.findall(text):
        if target.startswith("http://") or target.startswith("https://"):
            image_links.append(normalize_url(target))

    for target in HTML_LINK_RE.findall(text):
        html_links.append(normalize_url(target))

    for target in HTML_SRC_RE.findall(text):
        html_links.append(normalize_url(target))

    for target in URL_RE.findall(text):
        normalized = normalize_url(target)
        if normalized in markdown_links or normalized in image_links or normalized in html_links:
            continue
        naked_links.append(normalized)

    return {
        "markdown": markdown_links,
        "images": image_links,
        "html": html_links,
        "naked": naked_links,
    }


def plain_text_chars(body: str) -> int:
    body = INLINE_CODE_RE.sub(" ", body)
    body = MARKDOWN_IMAGE_RE.sub(r"\1 ", body)
    body = MARKDOWN_LINK_RE.sub(r"\1 ", body)
    body = URL_RE.sub(" ", body)
    body = HEADING_RE.sub("", body)
    body = WHITESPACE_RE.sub(" ", body)
    return len(body.strip())


def category_for(path: str, url_count: int, text_chars: int) -> str:
    if path.startswith("wiki/sources/"):
        return "generated_source_summary"
    if url_count == 0:
        return "no_external_links"
    if text_chars < 120:
        return "source_stub"
    if text_chars < 500 and url_count >= 2:
        return "link_collection"
    if text_chars < 2200:
        return "reference_note"
    return "deep_note_with_sources"


def recommendation_for(category: str, has_sources_field: bool, missing_sources_count: int) -> str:
    if category == "generated_source_summary":
        return "自动生成页，可保留；优先维护对应原始笔记。"
    if category == "source_stub":
        return "更像资料入口页；建议转为 source 管理，或在 raw/sources/web 中保留原文后把当前页精简为摘要。"
    if category == "link_collection":
        return "更像外链清单；建议拆成 source summaries + 对应 concept/entity 汇总页。"
    if category == "reference_note" and (not has_sources_field or missing_sources_count > 0):
        return "保留为 note，但应补齐 frontmatter.sources，并明确外链支撑了什么内容。"
    if category == "deep_note_with_sources" and (not has_sources_field or missing_sources_count > 0):
        return "是高价值笔记；建议保留并补 sources、aliases、wikilink。"
    if category in {"reference_note", "deep_note_with_sources"}:
        return "可保留为知识笔记，后续重点补 wikilink 和更细粒度 source summary。"
    return "无需处理。"


def analyze_file(root: Path, path: Path) -> dict[str, Any]:
    rel = repo_rel(root, path)
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    title = str(meta.get("title", "")).strip() or first_h1(body, path.stem)

    url_groups = collect_external_urls(raw)
    all_urls = []
    for urls in url_groups.values():
        all_urls.extend(urls)
    unique_urls = list(dict.fromkeys(all_urls))
    unique_domains = sorted({re.sub(r"^https?://", "", url).split("/", 1)[0] for url in unique_urls})

    fm_sources = meta.get("sources", [])
    fm_external_sources = [
        item for item in fm_sources if isinstance(item, str) and item.startswith(("http://", "https://"))
    ]
    missing_sources = [url for url in unique_urls if url not in fm_external_sources]
    text_chars = plain_text_chars(body)
    category = category_for(rel, len(unique_urls), text_chars)
    snippet = strip_markup_for_snippet(body)

    return {
        "path": rel,
        "title": title,
        "type": meta.get("type", ""),
        "category": category,
        "plain_text_chars": text_chars,
        "external_url_count": len(unique_urls),
        "external_markdown_links": len(url_groups["markdown"]),
        "external_image_links": len(url_groups["images"]),
        "external_naked_links": len(url_groups["naked"]),
        "external_html_links": len(url_groups["html"]),
        "domains": unique_domains,
        "frontmatter_external_sources": fm_external_sources,
        "missing_frontmatter_sources": missing_sources,
        "has_sources_field": isinstance(fm_sources, list) and len(fm_sources) > 0,
        "snippet": snippet,
        "recommendation": recommendation_for(
            category,
            isinstance(fm_sources, list) and len(fm_sources) > 0,
            len(missing_sources),
        ),
        "sample_urls": unique_urls[:5],
    }


def priority_score(entry: dict[str, Any]) -> tuple[int, int, int, str]:
    category_weight = {
        "source_stub": 0,
        "link_collection": 1,
        "reference_note": 2,
        "deep_note_with_sources": 3,
        "generated_source_summary": 4,
        "no_external_links": 5,
    }
    missing_penalty = 0 if entry["missing_frontmatter_sources"] else 1
    return (
        category_weight.get(entry["category"], 9),
        missing_penalty,
        -entry["external_url_count"],
        entry["path"],
    )


def render_summary(entries: list[dict[str, Any]], root: Path) -> str:
    category_counts = Counter(entry["category"] for entry in entries)
    domain_counts = Counter()
    for entry in entries:
        for domain in entry["domains"]:
            domain_counts[domain] += 1

    actionable = [
        entry
        for entry in entries
        if entry["category"] in {"source_stub", "link_collection", "reference_note", "deep_note_with_sources"}
        and not entry["path"].startswith("wiki/sources/")
    ]
    actionable.sort(key=priority_score)

    top_missing = [entry for entry in actionable if entry["missing_frontmatter_sources"]][:20]

    lines = [
        "# 外链体检报告",
        "",
        f"- 扫描仓库: `{root}`",
        f"- Markdown 文件数: `{len(entries)}`",
        f"- 含外链文件数: `{sum(1 for entry in entries if entry['external_url_count'] > 0)}`",
        f"- 生成时间: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        "- 说明: 当前报告只做仓库内结构扫描与分类，不做网页在线可达性检查。",
        "",
        "## 分类统计",
        "",
    ]

    for category, count in sorted(category_counts.items(), key=lambda item: item[0]):
        lines.append(f"- `{category}`: {count}")

    lines.extend(["", "## 高频域名", ""])
    for domain, count in domain_counts.most_common(20):
        lines.append(f"- `{domain}`: {count}")

    lines.extend(["", "## 优先处理清单", ""])
    if not actionable:
        lines.append("- 没有需要处理的外链文件。")
    else:
        for entry in actionable[:30]:
            lines.append(
                f"- `{entry['category']}` [{entry['path']}]({entry['path']}): "
                f"{entry['external_url_count']} 个外链，正文字符 {entry['plain_text_chars']}，建议：{entry['recommendation']}"
            )

    lines.extend(["", "## 待补 sources 字段", ""])
    if not top_missing:
        lines.append("- 没有发现缺失的 frontmatter.sources。")
    else:
        for entry in top_missing:
            lines.append(
                f"- [{entry['path']}]({entry['path']}): 缺少 {len(entry['missing_frontmatter_sources'])} 个外链来源入库"
            )

    lines.extend(["", "## 文件明细", ""])
    for entry in sorted(entries, key=priority_score):
        lines.append(f"### {entry['title']}")
        lines.append("")
        lines.append(f"- 路径: [{entry['path']}]({entry['path']})")
        lines.append(f"- 分类: `{entry['category']}`")
        lines.append(f"- 外链数: `{entry['external_url_count']}`")
        lines.append(f"- 正文字符数: `{entry['plain_text_chars']}`")
        lines.append(f"- 域名: `{', '.join(entry['domains'])}`" if entry["domains"] else "- 域名: 无")
        lines.append(f"- 建议: {entry['recommendation']}")
        if entry["snippet"]:
            lines.append(f"- 摘要: {entry['snippet']}")
        if entry["sample_urls"]:
            lines.append("- 示例外链:")
            for url in entry["sample_urls"]:
                lines.append(f"  - {url}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--out-md", default="reports/external_links_audit.md", help="markdown report path")
    parser.add_argument("--out-json", default="reports/external_links_audit.json", help="json report path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_md = (root / args.out_md).resolve()
    out_json = (root / args.out_json).resolve()
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.parts):
            continue
        if path.resolve() == out_md:
            continue
        entries.append(analyze_file(root, path))

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_md.write_text(render_summary(entries, root), encoding="utf-8")
    out_json.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    actionable = sum(
        1
        for entry in entries
        if entry["category"] in {"source_stub", "link_collection", "reference_note", "deep_note_with_sources"}
        and entry["external_url_count"] > 0
    )
    print(
        f"Wrote {args.out_md} and {args.out_json}; "
        f"scanned {len(entries)} markdown files, {actionable} actionable files"
    )


if __name__ == "__main__":
    main()
