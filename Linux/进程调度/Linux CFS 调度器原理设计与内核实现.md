---
title: Linux CFS 调度器：原理、设计与内核实现
type: note
status: active
tags: ["Linux", "进程调度", "CFS", "调度器", "vruntime"]
aliases: ["CFS调度器", "Completely Fair Scheduler"]
sources: ["http://arthurchiao.art/blog/linux-cfs-design-and-implementation-zh/"]
updated_at: 2026-05-01
---
# Linux CFS 调度器

CFS（Completely Fair Scheduler）于 Linux 2.6.23 引入，替代 O(1) 调度器。

## 核心思想

将物理 CPU 建模为理想多任务 CPU：N 个进程各得 1/N 的 CPU 时间。

## vruntime 机制

- `vruntime`：进程实际运行时间累计值（纳秒），决定调度顺序
- **永远选择 vruntime 最小的进程**运行
- `min_vruntime`：runqueue 中最小 vruntime，单调递增，新进程以此初始化
- 高优先级进程权重更大，vruntime 增长速度更慢 → 获得更多实际时间

## 红黑树组织

- 可运行进程按 vruntime 排序存入红黑树（`tasks_timeline`）
- 最左节点 = 下次调度目标（O(1) 查询）
- 插入 O(log N)

## 调度类架构

```c
struct sched_class {
    enqueue_task, dequeue_task, pick_next_task,
    task_tick, update_curr, check_preempt_curr, ...
};
```

三种 CFS 策略：**SCHED_NORMAL**（普通）、**SCHED_BATCH**（批处理）、**SCHED_IDLE**（最低优先级）

## 关键数据结构

| 结构 | 作用 |
|------|------|
| `task_struct.sched_class` | 指向调度类 |
| `sched_entity` | 调度实体（vruntime、load_weight） |
| `cfs_rq` | 每 CPU CFS 运行队列（含 tasks_timeline 红黑树） |
| `task_group` | 组调度（cgroup cpu.shares） |

## 调度周期

- `sched_latency`：调度周期 ~6ms
- `min_granularity_ns`：最小时间片，防过度切换
- 时间片 = sched_latency / nr_running（动态）

## CPU 带宽控制（cgroup）

- `cpu.cfs_period_us`：统计周期（100ms）
- `cpu.cfs_quota_us`：每周期 CPU 时间上限
- `cpu.stat`：nr_periods, nr_throttled, throttled_time

## 源码位置

`kernel/sched/fair.c` | `kernel/sched/rt.c` | `Documentation/scheduler/sched-design-CFS.rst`
