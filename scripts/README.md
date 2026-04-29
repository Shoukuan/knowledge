---
title: scripts
type: guide
status: active
tags: []
aliases: []
sources: []
updated_at: 2026-04-27
---
# scripts
包含用于仓库维护的小脚本。

- `normalize_frontmatter.py`：为 Markdown 文档补齐第一版知识库 frontmatter，不覆盖已存在的人工字段。
- `bootstrap_seed_knowledge.py`：补首批高价值主题的 `aliases/sources`，并生成第一批实体页、概念页和首页导航。
- `build_backlinks.py`：扫描 `wiki/` 页面的 wikilink 和 Markdown 链接，自动生成反向链接区块。
- `build_source_summaries.py`：根据 `wiki` 页面的 `sources` 字段生成 `wiki/sources/` 追溯页和资料索引。
- `audit_external_links.py`：扫描全仓库 Markdown 的网页外链，生成分类报告和可执行清单。
- `promote_source_stubs.py`：根据体检结果，批量把“纯外链入口页”补成结构化 source 页面。
- `generate_beautified_index.py`：生成带 frontmatter 元数据的仓库索引和搜索索引。
- `format_and_index.py`：规范 Markdown 标题并生成简版目录索引，不再插入 TOC。
- `find_large_files.py`：查找超过指定大小的文件并导出 CSV/Markdown 报告。

示例：

```
python scripts/find_large_files.py --path . --threshold 1 --out reports/large_files.csv --md
```

这会在 `reports/` 下生成 `large_files.csv` 和 `large_files.md`。

```bash
python scripts/bootstrap_seed_knowledge.py --root .
python scripts/build_source_summaries.py --root .
python scripts/build_backlinks.py --root .
python scripts/audit_external_links.py --root .
python scripts/promote_source_stubs.py --root .
python scripts/normalize_frontmatter.py --root .
python scripts/generate_beautified_index.py --root . --out docs/REPO_INDEX.md --search docs/search_index.json
```

这七步会更新主题地图、资料追溯页、反向链接、外链体检、source stub 升级、frontmatter，并重建浏览索引与搜索索引。
