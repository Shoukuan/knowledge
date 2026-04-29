---
title: Knowledge Base Schema
type: schema
status: active
tags: ["knowledge-base", "schema", "frontmatter"]
aliases: ["知识库规范", "仓库规则"]
sources: []
updated_at: 2026-04-27
---
# Knowledge Base Schema

## 目录结构

- `raw/sources/`: 原始资料，尽量保持不可变。
- `raw/assets/`: 图片、附件等静态资源。
- `wiki/index.md`: 知识目录与入口页。
- `wiki/log.md`: 结构化变更日志。
- `wiki/overview.md`: 当前知识库全局概览。
- `wiki/entities/`: 人物、组织、产品、工具等实体页。
- `wiki/concepts/`: 概念、机制、方法、协议等主题页。
- `wiki/sources/`: 对原始资料的摘要页。
- `wiki/queries/`: 有价值的问答、比较、总结沉淀。

## Frontmatter 规范

每个知识页优先使用以下字段：

- `title`: 页面标题，和 H1 对齐。
- `type`: 页面类型。第一版建议使用 `hub`、`note`、`guide`、`reference`、`index`、`overview`、`log`、`source`、`entity`、`concept`、`query`、`schema`、`purpose`。
- `status`: `active`、`seed`、`draft`、`archived` 之一。
- `tags`: 标签数组，优先来自目录层级和主题关键词。
- `aliases`: 别名数组，用于搜索召回和后续 wikilink 兼容。
- `sources`: 来源数组。现有手工笔记可先为空，后续从 `raw/sources/` 生成的页面再补充。
- `updated_at`: 最后一次结构化整理日期，格式 `YYYY-MM-DD`。

## 命名约定

- 页面内保持一个 H1 标题。
- 文件名尽量直接表达主题，不必为了格式强行改名。
- 目录用于承载主题上下文，标签会优先从目录路径派生。

## 链接约定

- 当前仓库先兼容标准 Markdown 链接。
- 当前已开始引入 `[[wikilink]]`，用于概念页、实体页和主题页之间的双向引用。
- 外部来源尽量在正文或 `sources` 中保留原始链接。
- `wiki/` 页面的反向链接由脚本自动生成，避免手工维护双向关系。

## 自动化原则

- 索引和搜索应优先读取 frontmatter，而不是只依赖文件名。
- 自动脚本默认补齐缺失元数据，不覆盖人工已写内容。
- 生成文件和手工维护文件尽量分层，避免相互覆盖。
- `wiki/sources/` 可由脚本根据 `sources` 引用自动生成，用于把主题页追溯到原始笔记。
