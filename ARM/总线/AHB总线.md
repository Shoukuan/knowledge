---
title: AHB 总线
type: note
status: active
tags: ["ARM", "AHB", "AMBA", "总线"]
aliases: ["AHB总线", "AMBA AHB", "Advanced High-performance Bus"]
sources: ["https://blog.csdn.net/zhoutaopower/article/details/103718009"]
updated_at: 2026-05-01
---
# AHB 总线

AHB（Advanced High-performance Bus）是 AMBA 规范中的高性能系统总线，用于 ARM 核与高速外设（RAM、DMA、NAND FLASH）之间的互连。

## 架构

三大部分：**Master** → **Infrastructure**（仲裁器 + 译码器 + 多路选择器） → **Slave**

## 核心特性

- Burst 传输、Split 事务、流水线操作
- 单时钟沿操作，无三态总线
- 支持 64/128 位数据总线
- 最多 16 个主机

## 关键信号

| 信号 | 方向 | 作用 |
|------|------|------|
| `HADDR[31:0]` | M→S | 地址总线 |
| `HTRANS[1:0]` | M→S | IDLE(00)/BUSY(01)/NONSEQ(10)/SEQ(11) |
| `HWRITE` | M→S | 1=写, 0=读 |
| `HSIZE[2:0]` | M→S | 传输大小 |
| `HBURST[2:0]` | M→S | 突发类型 |
| `HREADY` | S→M | 1=完成, 0=等待 |
| `HRESP[1:0]` | S→M | 00=OKAY, 01=ERROR, 10=RETRY, 11=SPLIT |

## 传输时序（两级流水线）

```
T1: 主机驱动地址+控制 ─── T2: 从机采样 ─── T3: 数据完成
                               │
                               └─ 主机可同时发下一笔地址
```

- HREADY 低时插入等待周期
- 写操作等待期间必须保持写数据不变

## 突发传输

| HBURST | 类型 | 说明 |
|--------|------|------|
| 000 | SINGLE | 单次 |
| 001 | INCR | 未定长度增量 |
| 010 | WRAP4 | 4拍回环 |
| 011 | INCR4 | 4拍增量 |
| 100-101 | WRAP8/INCR8 | 8拍 |
| 110-111 | WRAP16/INCR16 | 16拍 |

- 增量(INCR)：地址连续递增
- 回环(WRAP)：在地址边界处回环
- 禁止跨 1KB 边界

## 响应与仲裁

- **OKAY/ERROR**：完成或失败
- **RETRY**：主机重试，仲裁器保持优先级
- **SPLIT**：从机释放总线给其他主机

## 交叉链接

- [APB 总线](APB总线.md)
- [AXI 总线](AXI总线.md)
