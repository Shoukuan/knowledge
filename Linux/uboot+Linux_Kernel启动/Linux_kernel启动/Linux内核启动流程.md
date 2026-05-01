---
title: Linux 内核启动流程
type: note
status: active
tags: ["Linux", "内核", "启动", "boot", "start_kernel"]
aliases: ["Linux boot流程", "内核启动过程", "kernel boot sequence"]
sources: ["https://www.cnblogs.com/lcw/p/3337937.html"]
updated_at: 2026-05-01
---
# Linux 内核启动流程

ARM Linux 内核启动分四个阶段。

## 阶段一：自解压

内核镜像加载后先自解压，解压后的入口在 `arch/arm/kernel/head-armv.S` → `ENTRY(stext)`。

进入前处理器状态：r0=0, r1=架构编号, MMU关, D-cache关。

## 阶段二：内核引导（head-armv.S）

1. 设 SVC 模式，禁 FIQ/IRQ
2. `__lookup_processor_type()` → 检测 CPU ID，不匹配返回 `'p'`
3. `__lookup_architecture_type()` → 检测架构类型，不匹配返回 `'a'`
4. `__create_page_tables()` → 创建核心页表
5. 处理器特定初始化
6. `b start_kernel`

## 阶段三：start_kernel() 初始化链

| 函数 | 作用 |
|------|------|
| `lock_kernel()` | 获取大内核锁 |
| `setup_arch()` | 处理器/架构检测、内存布局、页表 |
| → `bootmem_init()` | 保留内核内存，标记可分配区域 |
| → `paging_init()` | 映射物理内存和 I/O 空间 |
| `parse_options()` | 解析内核命令行 |
| `trap_init()` | 拷贝异常向量表到 `vectors_base` |
| `init_IRQ()` | 初始化 irq_desc，设 mask/unmask |
| `sched_init()` | 初始化调度器 |
| `softirq_init()` | 初始化 tasklet |
| `time_init()` | 系统定时器 + 时钟中断 |
| `console_init()` | 尽早输出 |
| `sti()` | **开中断** |
| `calibrate_delay()` | 计算 BogoMIPS |
| `rest_init()` | 创建 init 线程 |

## 阶段四：init → 用户态

1. `do_basic_setup()` → 网络等初始化
2. `do_initcalls()` → 遍历 `.initcall.init` 段，逐个调用 `module_init()` 注册的函数
3. `execve("/sbin/init")` → 变为用户态 init
4. init 执行 `/etc/inittab`（或 BusyBox 的 `/etc/init.d/rcS`）

## 关键数据结构

- **meminfo**：物理内存布局（`nr_banks` + `bank[]`）
- **init_mm**：内核 mm_struct
- **swapper_pg_dir**：内核页目录（ARM 下 16KB）

## 交叉链接

- [start_kernel 介绍](start_kernel介绍.md)
- [Uboot 启动](../uboot/Uboot启动.md)
