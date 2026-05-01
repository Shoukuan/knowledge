---
title: RPC 远程过程调用
type: note
status: active
tags: ["RPC", "中间件", "分布式", "IPC", "Dubbo"]
aliases: ["远程过程调用", "Remote Procedure Call"]
sources: ["https://cloud.tencent.com/developer/article/1663930"]
updated_at: 2026-05-01
---
# RPC 远程过程调用

RPC 允许跨进程/跨机器调用函数，隐藏底层通信细节。

## 与本地调用的三个区别

1. **调用 ID 映射**：地址空间独立 → 用唯一 ID 替代函数指针，双方维护映射表
2. **序列化**：参数转二进制流传输，接收方反序列化
3. **网络传输**：通过 TCP/UDP 传输序列化数据

## 调用流程

```
Client → Client Stub（打包参数）→ 网络发送
  → Server OS 接收 → Server Stub（解包）→ 执行业务
  → Server Stub（打包结果）→ 网络返回
  → Client Stub（解包）→ 返回调用方
```

Stub 是透明性核心——让远程调用看起来像本地调用。

## Dubbo 架构

| 组件 | 职责 |
|------|------|
| 服务提供方 | 向注册中心注册服务 |
| 注册中心 | 存储服务信息，提供服务发现 |
| 服务调用方 | 通过 RPC 调用远程服务 |
| 监控中心 | 统计调用次数和耗时 |

## 同步 vs 异步

- **同步**：等待结果返回
- **异步**：不等待，回调通知，适合高吞吐场景
