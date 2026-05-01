---
title: Linux proc 文件系统
type: note
status: active
tags: ["Linux", "调试", "proc", "procfs", "性能分析"]
aliases: ["proc文件系统", "procfs", "/proc"]
sources: ["https://www.cnblogs.com/yungyu16/p/13193442.html"]
updated_at: 2026-05-01
---
# Linux proc 文件系统

/proc 是伪文件系统，数据驻留 RAM，动态反映内核运行状态。

## 核心系统文件

### CPU / 负载
| 文件 | 用途 |
|------|------|
| `cpuinfo` | 处理器信息 |
| `stat` | CPU 时间分布、上下文切换次数 |
| `loadavg` | 1/5/15 分钟负载均值 |
| `uptime` | 运行和空闲时间（秒） |

### 内存
| 文件 | 用途 |
|------|------|
| `meminfo` | 总内存/空闲/缓存/交换（free 命令数据源） |
| `vmstat` | 虚拟内存详细统计 |
| `zoneinfo` | 每 zone 水位线和页分布 |
| `slabinfo` | SLAB 缓存状态 |
| `buddyinfo` | 伙伴分配器碎片诊断 |

### I/O / 设备
| 文件 | 用途 |
|------|------|
| `diskstats` | 磁盘 I/O 统计 |
| `interrupts` | 每 CPU 中断分布 |
| `ioports` | 已注册 I/O 端口范围 |
| `iomem` | 物理设备内存映射 |
| `partitions` | 分区表 |
| `mounts` | 挂载点列表 |

### 内核信息
| 文件 | 用途 |
|------|------|
| `version` | 内核版本和编译参数 |
| `cmdline` | 内核启动参数 |
| `modules` | 已加载模块及依赖 |
| `kallsyms` | 内核符号表 |
| `kmsg` | 内核消息（dmesg 源） |
| `filesystems` | 支持的文件系统列表 |
| `crypto` | 加密算法信息 |

## 进程目录 (/proc/[pid]/)

| 文件 | 用途 |
|------|------|
| `cmdline` | 启动命令（僵尸进程为空） |
| `cwd` / `exe` / `root` | → 工作目录/可执行文件/根目录 |
| `fd/` | → 每个打开的文件描述符 |
| `maps` | 内存映射及权限 |
| `stat` / `status` | 进程状态（status 可读性更好） |
| `environ` | 环境变量 |
| `task/` | 线程信息（2.6+） |
| `limits` | 资源软/硬限制（2.6.24+） |

## /proc/sys/ — 内核参数调优

唯一可写的 /proc 区域。`echo VALUE > /proc/sys/.../file` 动态修改内核参数。注意不能用编辑器。

## 快速调试命令

```bash
cat /proc/meminfo          # 内存概览
cat /proc/stat             # 全局 CPU 统计
cat /proc/diskstats        # 磁盘 I/O
cat /proc/[pid]/status     # 进程详情
ls -l /proc/[pid]/fd/      # 进程打开的文件
cat /proc/[pid]/maps       # 进程内存布局
```

## 交叉链接

- [Linux 调试工具](Linux调试工具.md)
