---
title: QNX 进程间通信
type: note
status: active
tags: ["QNX", "IPC", "消息传递", "共享内存", "信号", "微内核"]
aliases: ["QNX IPC", "QNX进程间通信"]
sources: ["https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_sys_arch/ipc.html"]
updated_at: 2026-05-01
---
# QNX 进程间通信

QNX Neutrino 微内核中，消息传递是核心 IPC 原语。

## IPC 机制速查

| 机制 | 带宽 | 同步 | 适用 |
|------|------|------|------|
| 消息传递 | 近内存带宽 | 同步阻塞 | 通用 C/S |
| 脉冲 | 8bit code+32bit data | 非阻塞 | 中断通知 |
| 信号 | 低 | 异步 | POSIX 兼容 |
| 消息队列 | 中等 | 非阻塞 | 多生产者/消费者 |
| 共享内存 | 最高 | 无(需外部同步) | 大数据 |
| 管道/FIFO | 中等 | 阻塞I/O | 流式数据 |

## 同步消息传递

```c
MsgSend()     // 发送 → SEND-blocked → REPLY-blocked → READY
MsgReceive()  // 等待消息（无消息时 RECEIVE-blocked）
MsgReply()    // 回复 → 解除发送方阻塞
```

### 通道与连接

- **通道（Channel）**：服务器创建，用于接收
- **连接（Connection）**：客户端创建，映射为 FD

```c
chid = ChannelCreate(flags);
coid = ConnectAttach(nd, pid, chid, index, flags);
MsgSendv(coid, &iov, parts, &reply_iov, &rparts);
```

## 优先级继承

服务器处理消息时继承发送方优先级，防止优先级反转。

## 防死锁规则

1. 不让两个线程互相发消息
2. 组织为层级结构，发送方向朝上

## 脉冲

固定大小非阻塞消息，用于中断处理和轻量通知。

## 共享内存 + 消息传递组合

- 共享内存传大数据，消息传递传引用
- 本地用共享内存，远程用消息传递

## 信号（64 个）

1-40 传统 UNIX，41-56 POSIX 实时，57-64 QNX 专用（不可捕获，用于 `MsgDeliverEvent()`）
