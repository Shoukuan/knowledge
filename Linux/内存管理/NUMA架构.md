---
title: NUMA 架构
type: note
status: active
tags: ["Linux", "内存管理", "NUMA", "numactl"]
aliases: ["NUMA", "Non-Uniform Memory Access"]
sources: ["https://rianico.tech/numa-architecture.html"]
updated_at: 2026-05-01
---
# NUMA 架构

NUMA 给每个 CPU 独立的本地内存，避免多 CPU 争抢单一总线。

## 核心概念

- **NUMA Node**：每个物理 CPU + 本地内存抽象为一个节点
- **本地访问**：延迟低；**远程访问**：需跨节点
- 距离矩阵：local=10 vs remote=21（2 倍延迟差异）

## 查看拓扑

```bash
numactl -H       # 节点、CPU、内存大小、距离矩阵
numastat         # 每节点分配统计
```

## 分配策略

### 默认（本地优先）
本地内存耗尽时 → swap/回收，不用远程。**swap 代价往往 > 远程访问。**

### 交叉分配
```bash
numactl --interleave=all <cmd>  # 随机分散到所有节点
```

### 手动绑定
```bash
numactl -N 0 -m 0 <cmd>         # CPU 和内存绑 node 0
```

### zone_reclaim_mode
- `0`：优先用远程内存（推荐）
- `1`：本地回收优先

## numad

自动监控拓扑和资源使用，动态迁移进程。长运行负载可提升 **50%** 性能。短生命周期进程不适用。

## JVM

`-XX:+UseNUMA` — 为每个节点分配独立 Eden/Survivor 空间。
