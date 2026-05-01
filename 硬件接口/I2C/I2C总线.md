---
title: I2C 总线
type: note
status: active
tags: ["I2C", "总线", "协议", "硬件接口"]
aliases: ["I2C协议", "I2C bus", "I2C总线协议"]
sources: ["https://blog.csdn.net/guoguo295/article/details/41479353", "raw/sources/web/I2C总线.md"]
updated_at: 2026-05-01
---
# I2C 总线

I2C（Inter-Integrated Circuit）是 Philips 开发的二线制串行总线，广泛用于嵌入式设备与外设通信。

## 物理层

- **SDA**：串行数据线，双向
- **SCL**：串行时钟线，由主机驱动
- 空闲状态：两条线均被上拉电阻拉高
- 支持多主控，但同一时刻仅一个主机

## 协议时序

### 起始与停止
```
起始 S：SCL 高电平时，SDA 下降沿
停止 P：SCL 高电平时，SDA 上升沿
```

### 数据传输
- 每字节 8 位，大端序（MSB 先）
- SCL 高时 SDA 必须稳定，SDA 变化只能在 SCL 低时
- 每字节后跟 1 位 ACK：接收方拉低 SDA = ACK(0)，释放 SDA = NACK(1)

### 命令格式
首字节 = 7 位从机地址 + 1 位方向位（0=写，1=读）

## 典型读写序列

### 单字节写
`S → Addr+W → ACK → RegAddr → ACK → Data → ACK → P`

### 单字节读
`S → Addr+W → ACK → RegAddr → ACK → Sr → Addr+R → ACK → Data → NACK → P`

## 速率等级

| 模式 | 速率 | 典型应用 |
|------|------|----------|
| Standard | 100 Kbps | 传感器、RTC |
| Fast | 400 Kbps | EEPROM、PMIC |
| High-speed | 3.4 Mbps | 大容量存储 |

## 常见问题

### 总线死锁
**原因**：主机在通信中途异常复位，从机仍处于应答状态拉低 SDA。
**恢复**：主机在 SCL 上产生 9 个时钟脉冲，直到 SDA 被从机释放，然后发送停止信号。

### 地址冲突
多主控系统中，在起始信号后回读 SDA 做仲裁检测。丢失仲裁的主控立即释放总线转为从机。

## 交叉链接

- [I2C 驱动 (Linux)](../../Linux/驱动/I2C/i2c驱动.md)
- [SPI 总线](../SPI/SPI总线.md)
