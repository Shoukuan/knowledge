---
title: I2C 总线（原始存档）
type: source
status: active
tags: ["I2C", "总线", "协议", "raw"]
aliases: ["I2C protocol source"]
sources: ["https://blog.csdn.net/guoguo295/article/details/41479353"]
updated_at: 2026-05-01
---
# I2C 总线（原始存档）

> 来源：https://blog.csdn.net/guoguo295/article/details/41479353
> 存档时间：2026-05-01

## 基本特性

I2C 由 Philips 开发，两条线：**SDA**（数据）和 **SCL**（时钟）。空闲时均为高电平，大端传输，每次 8 位，支持多主控。

## 信号与时序

- **起始信号 S**：SCL 高时 SDA 下降沿
- **停止信号 P**：SCL 高时 SDA 上升沿
- **数据有效性**：SCL 高时 SDA 必须稳定，SDA 只能在 SCL 低时变化
- **应答 ACK**：接收方在第 9 个时钟拉低 SDA（ACK=0 表示应答，ACK=1 表示非应答）

## 寻址

命令字节 = 7 位从机地址 + 1 位 R/W（0=写，1=读），可扩展到 10 位。

## 读写流程

**写操作**：S → 地址+R/W=0 → ACK → 数据1 → ACK → ... → 数据N → ACK → P

**读操作**：S → 地址+R/W=1 → ACK → 数据1 → ACK → ... → 主机发 NACK → P

**读寄存器（两步）**：
1. 主机先写 command + 目标地址（实际是写操作）
2. 主机再读回数据

## 速率模式

| 模式 | 速率 |
|---|---|
| 标准模式 | 100 Kb/s |
| 快速模式 | 400 Kb/s |
| 高速模式 | 3.4 Mb/s |

## 总线死锁

**成因**：主机异常复位时 SCL 释放为高，但从机未复位，持续拉低 SDA 输出应答。主机复位后检测到 SDA=0 等待释放，从机等待 SCL 变低，形成死锁。

**解决**：从机电源可控 → 复位从机；从机侧监控程序主动释放；主机侧模拟 9 个 SCL 脉冲释放总线。
