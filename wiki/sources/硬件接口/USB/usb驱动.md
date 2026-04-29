---
title: 基于cherryUSB的USB驱动实现详解（资料摘要）
type: source
status: active
tags: ["source", "硬件接口", "USB"]
aliases: ["基于cherryUSB的USB驱动实现详解"]
sources: ["硬件接口/USB/usb驱动.md"]
updated_at: 2026-04-28
---
# 基于cherryUSB的USB驱动实现详解（资料摘要）

这是对 `硬件接口/USB/usb驱动.md` 的追溯页，用来连接原始笔记与当前知识地图。

## 原始位置

- [基于cherryUSB的USB驱动实现详解](../../../../硬件接口/USB/usb驱动.md)

## 摘要

cherryUSB 是一款开源、跨平台的 USB 协议栈，支持主机（Host）和设备（Device）模式，适用于多种 MCU/SoC 平台。其驱动实现以模块化、可移植为设计目标，便于适配不同硬件控制器。cherryUSB 驱动主要负责 USB 控制器的初始化、设备枚举、数据传输和中断处理等核心功能。    cherryUSB GitHub 代码库

## 结构线索

- 1. 概述
- 2. 驱动结构
- 3. 实现流程
  - 3.1 控制器初始化
    - 3.1.1 初始化流程概览
    - 3.1.2 关键代码与步骤说明
      - 3.1.2.1 HAL 层初始化
      - 3.1.2.2 端点资源初始化

## 关联 Wiki 页面

- [[USB]]

## 可点击导航

- [USB](../../../concepts/usb.md)

## 反向链接

<!-- BACKLINKS START -->
- [Source Index](../../index.md)
<!-- BACKLINKS END -->
