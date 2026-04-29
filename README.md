---
title: 个人知识库
type: hub
status: active
tags: ["knowledge-base", "wiki", "hub"]
aliases: ["Personal Knowledge Base", "PKB", "知识库首页"]
sources: ["purpose.md", "schema.md", "wiki/index.md"]
updated_at: 2026-04-28
---
# 个人知识库

这个仓库正在从“按目录存放资料”升级为“可搜索、可关联、可持续维护”的个人知识库。

## 快速入口

- [知识库目标](purpose.md)
- [知识库规范](schema.md)
- [Wiki 入口](wiki/index.md)
- [Wiki 总览](wiki/overview.md)
- [仓库索引](docs/REPO_INDEX.md)
- [搜索页面](docs/search.html)

## 首批主题地图

### 核心实体

- [Linux](wiki/entities/linux.md)
- [ARM](wiki/entities/arm.md)
- [RISC-V](wiki/entities/risc-v.md)
- [FreeRTOS](wiki/entities/freertos.md)
- [ThreadX](wiki/entities/threadx.md)
- [Buildroot](wiki/entities/buildroot.md)
- [OpenAMP](wiki/entities/openamp.md)
- [AUTOSAR](wiki/entities/autosar.md)
- [Trace32](wiki/entities/trace32.md)
- [QNX](wiki/entities/qnx.md)
- [NuttX](wiki/entities/nuttx.md)
- [DDS](wiki/entities/dds.md)
- [U-Boot](wiki/entities/u-boot.md)

### 核心概念

- [中断](wiki/concepts/中断.md)
- [GIC](wiki/concepts/gic.md)
- [设备树](wiki/concepts/设备树.md)
- [进程调度](wiki/concepts/进程调度.md)
- [内存管理](wiki/concepts/内存管理.md)
- [USB](wiki/concepts/usb.md)
- [PCIe](wiki/concepts/pcie.md)
- [IPC](wiki/concepts/ipc.md)
- [驱动模型](wiki/concepts/驱动模型.md)
- [启动流程](wiki/concepts/启动流程.md)
- [调试工具](wiki/concepts/调试工具.md)
- [RPC](wiki/concepts/rpc.md)
- [实时操作系统](wiki/concepts/实时操作系统.md)
- [I2C](wiki/concepts/i2c.md)
- [CAN](wiki/concepts/can.md)

## 当前内容范围

- Linux、RTOS、ARM、RISC-V
- 硬件接口与芯片基础设施
- 中间件、验证工具、调试工具
- 工作中沉淀的实践笔记与问题总结

## 维护方式

- 现有 Markdown 已统一纳入 frontmatter 规范。
- `docs/search.html` 基于标题、路径、标签和别名提供静态搜索。
- `wiki/` 目录承载逐步提炼出来的实体页、概念页和高价值问答。

## 下一阶段

- 扩展第二批实体页和概念页，补更多 `aliases` / `sources`。
- 逐步引入 `[[wikilink]]`、反向链接和主题聚合页。
- 基于现有 frontmatter 与索引，继续增强自动问答和知识图谱能力。
