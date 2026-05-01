---
title: ARM 异常和中断处理（原始存档）
type: source
status: active
tags: ["ARM", "异常", "中断", "raw"]
aliases: ["ARM exception and interrupt handling source"]
sources: ["https://willendless.github.io/体系结构/2021/03/11/ARM架构2/"]
updated_at: 2026-05-01
---
# ARM 异常和中断处理（原始存档）

> 来源：https://willendless.github.io/体系结构/2021/03/11/ARM架构2/
> 存档时间：2026-05-01

## 异常的定义与分类

ARM架构将异常定义为要求内核处理或提供服务的系统事件。分为两大类：

### 同步异常（Synchronous）
由直接执行某条指令导致，返回地址指向引发异常的指令位置。

### 异步异常（Asynchronous）
由外部事件或信号触发，包含三种子类型：
- **IRQ** — 通用中断请求
- **FIQ** — 快速中断请求，优先级高于IRQ
- **SError（System Error）** — 通常由异步数据终止导致

## 导致异常的动作

- **Aborts**：Instruction Aborts（取指令错误）和 Data Aborts（数据访问错误）
- **Reset**：最高异常级别，不可被屏蔽，复位向量地址从 `RVBAR_ELn` 读取
- **异常生成指令**：SVC（User→EL1）、HVC（Guest OS→EL2）、SMC（Normal World→Secure World）
- **Interrupts**：IRQ/FIQ 通过中断控制器仲裁后送给处理器核

## 异常向量表

EL3、EL2、EL1 各有独立向量表，地址存放在 `VBAR_ELx`。共 16 个向量，每个固定 64 字节（0x80）。

4 个异常类型 × 4 个执行模式：
- 异常类型：Synchronous(0)、IRQ(1)、FIQ(2)、SError(3)
- 执行模式：Current EL with SP0、Current EL with SPx、Lower EL using AArch64、Lower EL using AArch32

## 处理器自动操作

1. 保存 PSTATE → SPSR
2. 更新 PSTATE
3. 返回地址 → ELR
4. 跳转到向量表

## 关键寄存器

| 寄存器 | 功能 |
|---|---|
| VBAR_ELn | 异常向量表基地址 |
| SPSR_ELn | 保存异常前的 PSTATE |
| ELR_ELn | 异常返回地址 |
| ESR_ELn | 异常原因综合症（EC/IL/ISS） |
| FAR_ELn | 错误虚拟地址（同步异常） |
| DAIF | 中断掩码域 |
| SCR_EL3 / HCR_EL2 | 异常路由控制 |

## 与 x86 对比

| 概念 | x86 | ARM |
|---|---|---|
| Interrupt | 异步事件 | IRQ/FIQ |
| Exception | 同步事件 | 同步异常 |
| Fault | 指令未执行（page fault） | Abort 的一种 |
| Trap | 陷阱指令（breakpoint） | 异常生成指令 |
| Abort | 无法恢复（machine check） | SError |
