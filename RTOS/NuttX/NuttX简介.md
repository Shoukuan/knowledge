---
title: NuttX 简介
type: note
status: active
tags: ["NuttX", "RTOS", "POSIX", "嵌入式"]
aliases: ["NuttX RTOS", "NuttX实时操作系统"]
sources: ["https://juejin.cn/post/7321993405414932531"]
updated_at: 2026-05-01
---
# NuttX 简介

NuttX 是兼容 POSIX 的 RTOS，设计接近 Linux 但资源要求极低。

## 核心特点

- **原生 POSIX**：可商用 RTOS 中唯一原生完整 POSIX API
- **极小体积**：最小 < 32KB，最大 < 256KB
- **完全可裁剪**：Kconfig（`make menuconfig`）
- **Linux 兼容**：API 接近 Linux，开源软件易移植

## 架构

| 子系统 | 能力 |
|--------|------|
| 调度 | pthread、信号量、消息队列、SMP/AMP、tickless |
| 文件系统 | VFS、FAT/LittleFS/NFS/ROMFS 等十余种 |
| 网络 | 以太网/WiFi/BLE/CAN、IPv4/IPv6、BSD socket |
| 驱动 | 类 Linux 字符设备接口、低功耗框架 |

## 启动流程

```
POWERUP(0) → BOOT(1) → TASKLISTS(2) → MEMORY(3)
  → HARDWARE(4) → OSREADY(5) → IDLELOOP(6)
```

## NSH

类似 bash 的 shell，支持脚本、程序加载、系统挂载。

## 对比

| | Linux | NuttX |
|------|------|------|
| POSIX | ✅ | ✅（原生） |
| 内存 | MB~GB | < 256KB |
| MMU | 需要 | 可选 |
