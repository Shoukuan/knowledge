---
title: I2C驱动（资料摘要）
type: source
status: active
tags: ["source", "Linux", "驱动", "I2C"]
aliases: ["I2C驱动"]
sources: ["Linux/驱动/I2C/i2c驱动.md"]
updated_at: 2026-04-28
---
# I2C驱动（资料摘要）

这是对 `Linux/驱动/I2C/i2c驱动.md` 的追溯页，用来连接原始笔记与当前知识地图。

## 原始位置

- [I2C驱动](../../../../../Linux/驱动/I2C/i2c驱动.md)

## 摘要

I2C总线对应这/bus下的一条总线，这个I2C总线结构体管理着I2C设备与I2C驱动的匹配，删除等操作，当设备或者驱动注册到总线时，I2C总线会调用i2c_device_match函数查看I2C设备和驱动是否匹配，如果匹配则调用i2c_device_probe函数 ，进而调用I2C驱动的probe函数。

## 结构线索

  - I2C总线
  - I2C驱动
  - I2C设备
  - I2C适配器

## 关联 Wiki 页面

- [[I2C]]

## 可点击导航

- [I2C](../../../../concepts/i2c.md)

## 反向链接

<!-- BACKLINKS START -->
- [Source Index](../../../index.md)
<!-- BACKLINKS END -->
