#!/usr/bin/env python3
"""Helpers for reading and writing simple YAML frontmatter."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def split_frontmatter(text: str) -> Tuple[Dict[str, object], str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    meta: Dict[str, object] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            meta[key] = ""
            continue
        if value.startswith("[") and value.endswith("]"):
            try:
                meta[key] = json.loads(value)
                continue
            except json.JSONDecodeError:
                inner = value[1:-1].strip()
                meta[key] = [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
                continue
        if value in {"true", "false"}:
            meta[key] = value == "true"
            continue
        meta[key] = value.strip("\"'")
    return meta, text[match.end():]


def dump_frontmatter(meta: Dict[str, object]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        if isinstance(value, list):
            rendered = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines)


def title_from_body(body: str, path: Path) -> str:
    match = H1_RE.search(body)
    if match:
        return match.group(1).strip()

    stem = path.stem.replace("_", " ").replace("-", " ").strip()
    return stem or path.name


def ensure_h1(body: str, title: str) -> str:
    body = body.lstrip("\n")
    if H1_RE.search(body):
        return body
    if not body:
        return f"# {title}\n"
    return f"# {title}\n\n{body}"


def strip_markup_for_snippet(body: str) -> str:
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"^#.*$", "", body, flags=re.M)
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", body)
    body = re.sub(r"\[\[([^\]]+)\]\]", r"\1", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    paragraphs = [part.strip().replace("\n", " ") for part in body.split("\n\n")]
    for paragraph in paragraphs:
        if paragraph:
            return paragraph[:240]
    return ""


def parse_wikilinks(body: str) -> List[str]:
    links: List[str] = []
    for raw in WIKILINK_RE.findall(body):
        target = raw.split("|", 1)[0].strip()
        if target:
            links.append(target)
    return links


def parse_markdown_links(body: str) -> List[Tuple[str, str]]:
    links: List[Tuple[str, str]] = []
    for label, target in MARKDOWN_LINK_RE.findall(body):
        links.append((label.strip(), target.strip()))
    return links


def clean_tag(value: str) -> str:
    value = value.strip().replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value)
    return value


def tags_from_path(path: Path) -> List[str]:
    skip = {"docs", "scripts", "wiki", "raw", "sources", "assets"}
    tags: List[str] = []
    for part in path.parts[:-1]:
        tag = clean_tag(part)
        if not tag or tag.lower() in skip:
            continue
        if tag not in tags:
            tags.append(tag)
    return tags
