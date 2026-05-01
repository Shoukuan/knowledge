---
title: IPC
type: concept
status: active
tags: ["concept", "IPC", "中间件"]
aliases: ["Inter Process Communication", "进程间通信", "消息通信"]
sources: ["中间件/QNX/IPC.md", "中间件/RPC/分布式通信技术之远程调用：RPC.md", "中间件/OpenAMP/OpenAMP.md", "中间件/RpMSG/RpMSG Lite.md"]
updated_at: 2026-04-28
---
# IPC

IPC 在当前知识库里跨本地 OS 通信、分布式调用和异构多核消息传递三类场景。

## 核心问题

- 本地 IPC 与分布式 RPC 的抽象边界是什么
- OpenAMP/RPMsg 如何解决异构核间通信
- 不同 IPC 模型各自适合怎样的实时性与解耦需求

## 相关资料

- [IPC](https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_sys_arch/ipc.html)
- [分布式通信技术之远程调用：RPC](https://cloud.tencent.com/developer/article/1663930)
- [OpenAMP](https://github.com/OpenAMP)
- [RpMSG Lite](../../中间件/RpMSG/RpMSG Lite.md)

## 主题连接

- [[OpenAMP]]

## 延伸链接

- [OpenAMP](../entities/openamp.md)

## 反向链接

<!-- BACKLINKS START -->
- [RPC](rpc.md)
- [DDS](../entities/dds.md)
- [OpenAMP](../entities/openamp.md)
- [QNX](../entities/qnx.md)
- [OpenAMP（资料摘要）](../sources/中间件/OpenAMP/OpenAMP.md)
- [IPC（资料摘要）](../sources/中间件/QNX/IPC.md)
- [分布式通信技术之远程调用：RPC（资料摘要）](../sources/中间件/RPC/分布式通信技术之远程调用：RPC.md)
- [RPMSG Lite（资料摘要）](../sources/中间件/RpMSG/RpMSG Lite.md)
<!-- BACKLINKS END -->
