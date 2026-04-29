# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

This is a **personal knowledge base** for embedded systems, chip infrastructure, and engineering practice. Content covers Linux, RTOS, ARM, RISC-V, hardware interfaces, middleware, verification tools, and debugging workflows.

The repo is being upgraded from flat "notes in directories" into a **searchable, linkable, sustainably-maintained wiki** with YAML frontmatter, backlinks, entity/concept pages, and static search.

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `wiki/` | Curated wiki pages |
| `wiki/entities/` | Entity pages: Linux, ARM, RISC-V, FreeRTOS, ThreadX, OpenAMP, AUTOSAR, etc. |
| `wiki/concepts/` | Concept pages: interrupts, GIC, memory management, USB, PCIe, IPC, DTS, scheduling, etc. |
| `wiki/sources/` | Traced pages linking wiki content back to original sources |
| `wiki/queries/` | Q&A, comparisons, summaries |
| `scripts/` | Python automation scripts |
| `docs/` | Generated docs: search index, repo index, GitHub Pages deployment |
| `工程实践/` | Engineering practice notes: Git, VIM, Markdown, tools |
| `专业书籍/` | Reference books (PDFs stored locally, not in git) |
| `仿真工具/` | SI/PI simulation tools: SIwave, HFSS (PDFs/ZIPs local only) |
| `智能手表/` | Smartwatch reference projects (ZIPs local only) |
| Root category dirs | Linux/, ARM/, RTOS/, RiscV/, 存储/, 算法/, 硬件接口/, 中间件/, 验证工具/, Trace32/ — flat markdown notes |

## Frontmatter Schema

Every wiki page uses YAML frontmatter. Scripts read frontmatter first, not just filenames:

```yaml
---
title: "Page Title"          # Aligned with H1 heading
type: hub|note|guide|reference|index|overview|log|source|entity|concept|query|schema|purpose|backlink
status: active|seed|draft|archived
tags: ["tag1", "tag2"]       # Derived from directory path + topic keywords
aliases: ["alternative name"]# For search recall and wikilink compatibility
sources: ["original source URL or file path"]
updated_at: 2026-04-28        # ISO date, last structured update
---
```

**Rules:**
- Scripts fill missing metadata without overwriting manual edits.
- Generated files and manually-maintained files are kept in separate layers.
- Index and search scripts always read frontmatter first.

## Automation Scripts

All scripts are in `scripts/` (Python):

| Script | Purpose |
|--------|---------|
| `format_and_index.py` | Normalize markdown frontmatter and generate `docs/REPO_INDEX.md` |
| `normalize_frontmatter.py` | Audit and fix YAML frontmatter across all markdown files |
| `generate_beautified_index.py` | Generate categorized, collapsible repo index with search |
| `bootstrap_seed_knowledge.py` | Seed wiki pages from existing flat markdown notes |
| `build_backlinks.py` | Build reverse links between wiki pages |
| `build_source_summaries.py` | Generate wiki/sources/ summary pages from source materials |
| `promote_source_stubs.py` | Promote source stubs to full wiki pages |
| `audit_external_links.py` | Audit external links for broken/dead URLs |
| `find_large_files.py` | Find large files in the repository |

Additional Python scripts:
| Script | Purpose |
|--------|---------|
| `frontmatter_utils.py` | Shared utilities for frontmatter parsing and manipulation |

### GitHub CI/CD
| File | Purpose |
|------|---------|
| `.github/workflows/deploy-docs.yml` | Auto-deploy `docs/` to `gh-pages` branch on push to `master` (or manual trigger) |

## Content Domains

Main technical domains covered:
- **Linux**: kernel internals, boot flow, process scheduling, memory management, interrupts, drivers, DTS, debugging
- **ARM**: Core architecture (lock-step/split-step), GIC/GIC600, CoreSight
- **RISC-V**: base ISA, interrupts (PLIC/CLINT), boot sequences, riscv-dv
- **RTOS**: FreeRTOS, ThreadX, NuttX
- **Hardware Interfaces**: USB (enumeration, descriptors, DFU, fastboot), SPI, PCIe, I2C, CAN
- **Middleware**: OpenAMP, AutoSAR, DDS, RPC, QNX IPC, RpMSG/Virtio, DMA-BUF
- **Verification Tools**: ZEBU+VDK, Palladium+Helium, TCL, Trace32
- **Storage**: DDR/SDRAM, DDR firmware
- **Simulation**: SI/PI simulation (SIwave, HFSS), package/PCB extraction
- **Engineering Practice**: Git, VIM, Markdown, performance optimization

## Development Workflow

### GitHub Pages
- Deployed via `.github/workflows/deploy-docs.yml` — pushes `docs/` to `gh-pages` branch
- Static search lives at `docs/search.html`

### Adding New Content
1. Write the markdown note in the appropriate category directory
2. Add YAML frontmatter following the schema above
3. Run the format-and-index script:
   ```bash
   python3 scripts/format_and_index.py
   ```

### Wiki Page Generation
1. Run seed knowledge bootstrap:
   ```bash
   python3 scripts/bootstrap_seed_knowledge.py
   ```
2. Build backlinks:
   ```bash
   python3 scripts/build_backlinks.py
   ```

## Important Conventions

- **Naming**: Chinese filenames are used throughout; do not rename them without explicit instruction.
- **Frontmatter**: Always preserve existing frontmatter; only fill in missing fields.
- **Links**: Use standard Markdown links. `[[wikilinks]]` are being gradually introduced.
- **H1**: Each page has exactly one H1 heading, aligned with `title` in frontmatter.
- **Raw materials**: Content in `raw/` should be treated as read-only originals.
- **Binary files**: PDFs and ZIPs are excluded from git tracking via `.gitignore`. Store them externally (NAS, cloud drive) or locally outside the repo. Images (PNG/JPG) used in documentation are tracked.
