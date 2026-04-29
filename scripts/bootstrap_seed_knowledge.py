#!/usr/bin/env python3
"""
Bootstrap first-batch entity/concept pages and enrich selected note metadata.

Usage:
    python scripts/bootstrap_seed_knowledge.py --root .
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from posixpath import relpath

from frontmatter_utils import dump_frontmatter, ensure_h1, split_frontmatter, title_from_body


TODAY = date.today().isoformat()

SEED_NOTES = {
    "Linux/Linux内核.md": {
        "aliases": ["Linux kernel", "Linux Kernel", "Kernel"],
        "sources": ["https://linux-kernel-labs-zh.xyz/lectures/intro.html"],
        "tags": ["Linux", "内核"],
    },
    "ARM/GIC/GIC.md": {
        "aliases": ["Generic Interrupt Controller", "ARM GIC"],
        "sources": ["ARM/GIC/GIC600/gic_600.md", "ARM/架构/异常和中断处理.md"],
        "tags": ["ARM", "GIC", "中断"],
    },
    "Linux/驱动/DTS/Device Tree：基本概念.md": {
        "aliases": ["Device Tree", "设备树", "DT"],
        "sources": ["http://www.wowotech.net/device_model/dt_basic_concept.html"],
        "tags": ["Linux", "驱动", "DTS", "设备树"],
    },
    "Linux/进程调度/linux进程调度.md": {
        "aliases": ["Linux 调度", "Linux scheduler", "进程调度"],
        "sources": ["https://dreamgoing.github.io/linux%E8%BF%9B%E7%A8%8B%E8%B0%83%E5%BA%A6.html"],
        "tags": ["Linux", "进程调度", "调度器"],
    },
    "Linux/内存管理/内存管理总结.md": {
        "aliases": ["Linux 内存管理", "Memory Management"],
        "sources": ["Linux/内存管理/Linux内存管理初始化.md", "Linux/内存管理/细说mmap系统调用.md"],
        "tags": ["Linux", "内存管理"],
    },
    "硬件接口/USB/USB协议.md": {
        "aliases": ["USB protocol", "通用串行总线", "USB 2.0"],
        "sources": ["https://www.usbzh.com/article/detail-607.html", "https://www.usbzh.com/article/detail-110.html"],
        "tags": ["硬件接口", "USB", "协议"],
    },
    "硬件接口/PCIe/PCIe.md": {
        "aliases": ["PCI Express", "Peripheral Component Interconnect Express"],
        "sources": ["https://r12f.com/posts/pcie-1-basics/", "硬件接口/PCIe/Linux PCIe源码解析.md"],
        "tags": ["硬件接口", "PCIe", "总线"],
    },
    "中间件/OpenAMP/OpenAMP.md": {
        "aliases": ["Open Asymmetric Multi Processing", "RemoteProc", "RPMsg"],
        "sources": ["https://github.com/OpenAMP", "中间件/RpMSG/RpMSG Lite.md", "中间件/RpMSG/Virtio 原理与实现.md"],
        "tags": ["中间件", "OpenAMP", "IPC"],
    },
    "Linux/buildroot/buildroot概述及使用.md": {
        "aliases": ["Buildroot", "buildroot"],
        "sources": ["https://blog.51cto.com/knifeedge/5136296", "Linux/buildroot/buildroot使用介绍.md"],
        "tags": ["Linux", "Buildroot", "构建系统"],
    },
    "RTOS/FreeRTOS/Freertos使用.md": {
        "aliases": ["FreeRTOS", "freertos", "RTOS"],
        "sources": ["https://doc.embedfire.com/rtos/freertos/zh/latest/index.html", "https://freertos.org/zh-cn-cmn-s/a00106.html"],
        "tags": ["RTOS", "FreeRTOS"],
    },
    "RiscV/基础指令集.md": {
        "aliases": ["RISC-V ISA", "RV32I", "RV64I"],
        "sources": ["RiscV/(RISCV) RISC-V System, Booting, And Interrupts.md"],
        "tags": ["RiscV", "指令集", "ISA"],
    },
    "Trace32/调试工具-Trace32.md": {
        "aliases": ["TRACE32", "Lauterbach Trace32", "Lauterbach"],
        "sources": ["https://www.dumpstack.cn/index.php/2022/02/25/398.html#37"],
        "tags": ["Trace32", "调试工具"],
    },
    "中间件/AutoSAR/万字长文解读AUTOSAR完整架构及AP特性.md": {
        "aliases": ["AUTOSAR", "AUTOSAR AP", "Classic Platform", "Adaptive Platform"],
        "sources": ["https://zhuanlan.zhihu.com/p/536367959"],
        "tags": ["中间件", "AUTOSAR", "汽车软件"],
    },
    "RTOS/NuttX/NuttX简介.md": {
        "aliases": ["NuttX", "Apache NuttX"],
        "sources": ["https://juejin.cn/post/7321993405414932531"],
        "tags": ["RTOS", "NuttX"],
    },
    "中间件/QNX/IPC.md": {
        "aliases": ["QNX IPC", "QNX Neutrino IPC", "Interprocess Communication"],
        "sources": ["https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_sys_arch/ipc.html"],
        "tags": ["中间件", "QNX", "IPC"],
    },
    "中间件/DDS/分布式实时通信—DDS概述.md": {
        "aliases": ["DDS", "Data Distribution Service"],
        "sources": ["https://blog.yanjingang.com/?p=6716", "中间件/DDS/分布式实时通信—DDS进阶.md"],
        "tags": ["中间件", "DDS", "通信中间件"],
    },
    "Linux/uboot+Linux_Kernel启动/Linux_kernel启动/Linux内核启动流程.md": {
        "aliases": ["Linux boot flow", "start_kernel", "Linux 启动流程"],
        "sources": ["https://www.cnblogs.com/lcw/p/3337937.html", "Linux/uboot+Linux_Kernel启动/Linux_kernel启动/start_kernel介绍.md"],
        "tags": ["Linux", "启动", "boot"],
    },
    "Linux/调试/Linux调试工具.md": {
        "aliases": ["Linux debugging tools", "gdb", "perf", "ftrace"],
        "sources": ["https://cloud.tencent.com/developer/article/1471057", "https://linuxtools-rst.readthedocs.io/zh-cn/latest/advance/02_program_debug.html"],
        "tags": ["Linux", "调试", "工具"],
    },
    "中间件/RPC/分布式通信技术之远程调用：RPC.md": {
        "aliases": ["Remote Procedure Call", "RPC", "远程调用"],
        "sources": ["https://cloud.tencent.com/developer/article/1663930"],
        "tags": ["中间件", "RPC", "通信"],
    },
    "硬件接口/I2C/I2C总线.md": {
        "aliases": ["Inter-Integrated Circuit", "I2C bus"],
        "sources": ["https://blog.csdn.net/guoguo295/article/details/41479353", "Linux/驱动/I2C/i2c驱动.md"],
        "tags": ["硬件接口", "I2C", "总线"],
    },
    "硬件接口/CAN/CAN协议.md": {
        "aliases": ["Controller Area Network", "CAN bus"],
        "sources": ["https://www.cnblogs.com/pejoicen/p/3986587.html", "https://zhuanlan.zhihu.com/p/162708070"],
        "tags": ["硬件接口", "CAN", "总线"],
    },
}

ENTITY_PAGES = {
    "wiki/entities/linux.md": {
        "title": "Linux",
        "aliases": ["Linux 内核", "Linux kernel"],
        "tags": ["entity", "Linux", "kernel"],
        "sources": ["Linux/Linux内核.md", "Linux/Linux嵌入式系统开发.md", "Linux/linux_kernel_wiki.md"],
        "summary": "Linux 是当前知识库中的核心技术主线，覆盖内核结构、启动流程、调试、驱动、内存管理和调度等多个主题。",
        "focus": ["内核启动与初始化", "进程调度与中断处理", "驱动模型与设备树", "调试与性能分析"],
        "seealso": ["wiki/concepts/中断.md", "wiki/concepts/设备树.md", "wiki/concepts/进程调度.md", "wiki/concepts/内存管理.md"],
    },
    "wiki/entities/arm.md": {
        "title": "ARM",
        "aliases": ["ARM Architecture", "ARMv8", "ARM64"],
        "tags": ["entity", "ARM", "architecture"],
        "sources": ["ARM/架构/ARM寄存器简介.md", "ARM/架构/异常和中断处理.md", "ARM/汇编指令/ARM64汇编.md"],
        "summary": "ARM 是当前仓库里与 SoC、异常处理、总线、GIC 和调试链路高度关联的一条主线。",
        "focus": ["异常与中断", "寄存器与指令", "总线与片上调试", "GIC 与多核系统"],
        "seealso": ["wiki/concepts/gic.md", "wiki/concepts/中断.md"],
    },
    "wiki/entities/risc-v.md": {
        "title": "RISC-V",
        "aliases": ["RiscV", "RISC-V ISA"],
        "tags": ["entity", "RiscV", "ISA"],
        "sources": ["RiscV/基础指令集.md", "RiscV/中断/plic_clint.md", "RiscV/(RISCV) RISC-V System, Booting, And Interrupts.md"],
        "summary": "RISC-V 在知识库中主要覆盖基础指令集、启动流程和中断控制相关内容。",
        "focus": ["基础指令集", "启动与引导", "PLIC/CLINT 中断模型"],
        "seealso": ["wiki/concepts/中断.md"],
    },
    "wiki/entities/freertos.md": {
        "title": "FreeRTOS",
        "aliases": ["freertos", "RTOS"],
        "tags": ["entity", "FreeRTOS", "RTOS"],
        "sources": ["RTOS/FreeRTOS/Freertos使用.md", "RTOS/FreeRTOS/内存管理.md", "RTOS/Freertos和Threadx.md"],
        "summary": "FreeRTOS 是当前 RTOS 分支中的主要对象，重点围绕任务、内存管理和与 ThreadX 的比较。",
        "focus": ["任务调度", "内存管理", "与 ThreadX 的差异"],
        "seealso": ["wiki/entities/threadx.md"],
    },
    "wiki/entities/threadx.md": {
        "title": "ThreadX",
        "aliases": ["Azure RTOS ThreadX", "threadx"],
        "tags": ["entity", "ThreadX", "RTOS"],
        "sources": ["RTOS/ThreadX/ThreadX文档.md", "RTOS/Freertos和Threadx.md"],
        "summary": "ThreadX 在知识库中作为 RTOS 对照对象存在，适合和 FreeRTOS 一起比较接口、调度和使用方式。",
        "focus": ["文档入口", "调度与 API", "与 FreeRTOS 的差异"],
        "seealso": ["wiki/entities/freertos.md"],
    },
    "wiki/entities/buildroot.md": {
        "title": "Buildroot",
        "aliases": ["buildroot"],
        "tags": ["entity", "Buildroot", "构建系统"],
        "sources": ["Linux/buildroot/buildroot概述及使用.md", "Linux/buildroot/buildroot使用介绍.md", "Linux/buildroot/The Buildroot user manual.md"],
        "summary": "Buildroot 是嵌入式 Linux 构建链条中的关键工具，当前知识库已积累概述、构建指南和官方手册入口。",
        "focus": ["构建流程", "包管理与配置", "嵌入式系统交付"],
        "seealso": ["wiki/entities/linux.md"],
    },
    "wiki/entities/openamp.md": {
        "title": "OpenAMP",
        "aliases": ["RemoteProc", "RPMsg", "Open Asymmetric Multi Processing"],
        "tags": ["entity", "OpenAMP", "IPC"],
        "sources": ["中间件/OpenAMP/OpenAMP.md", "中间件/RpMSG/RpMSG Lite.md", "中间件/RpMSG/Virtio 原理与实现.md"],
        "summary": "OpenAMP 是异构多核系统中的通信框架，在知识库中与 RPMsg、Virtio 和远程处理器通信密切相关。",
        "focus": ["异构多核通信", "RPMsg/Virtio 协议栈", "RemoteProc 与资源管理"],
        "seealso": ["wiki/concepts/ipc.md"],
    },
    "wiki/entities/autosar.md": {
        "title": "AUTOSAR",
        "aliases": ["AUTOSAR AP", "AUTOSAR CP", "Adaptive Platform", "Classic Platform"],
        "tags": ["entity", "AUTOSAR", "汽车软件"],
        "sources": ["中间件/AutoSAR/万字长文解读AUTOSAR完整架构及AP特性.md"],
        "summary": "AUTOSAR 是汽车软件架构领域的重要对象，当前知识库已经有一篇较系统的结构综述作为入口。",
        "focus": ["Classic/Adaptive 架构", "分层设计", "汽车软件生态"],
        "seealso": ["wiki/entities/openamp.md"],
    },
    "wiki/entities/trace32.md": {
        "title": "Trace32",
        "aliases": ["TRACE32", "Lauterbach Trace32", "Lauterbach"],
        "tags": ["entity", "Trace32", "调试工具"],
        "sources": ["Trace32/调试工具-Trace32.md"],
        "summary": "Trace32 是当前知识库中代表性的芯片级调试工具，内容聚焦寄存器视图、脚本语法和调试工作流。",
        "focus": ["调试脚本", "寄存器与外设观察", "芯片级调试协作"],
        "seealso": ["wiki/entities/arm.md", "wiki/entities/linux.md"],
    },
    "wiki/entities/qnx.md": {
        "title": "QNX",
        "aliases": ["QNX Neutrino", "QNX SDP"],
        "tags": ["entity", "QNX", "RTOS"],
        "sources": ["中间件/QNX/IPC.md"],
        "summary": "QNX 在当前知识库中主要以实时操作系统和消息驱动 IPC 模型为切入点，适合和 Linux、RTOS 分支形成对照。",
        "focus": ["消息传递式 IPC", "微内核实时系统", "和 Linux/RTOS 的对照学习"],
        "seealso": ["wiki/concepts/ipc.md", "wiki/concepts/实时操作系统.md"],
    },
    "wiki/entities/nuttx.md": {
        "title": "NuttX",
        "aliases": ["Apache NuttX", "NuttX RTOS"],
        "tags": ["entity", "NuttX", "RTOS"],
        "sources": ["RTOS/NuttX/NuttX简介.md"],
        "summary": "NuttX 是当前 RTOS 分支中的另一条操作系统主线，适合与 FreeRTOS、ThreadX 一起形成嵌入式 OS 对照视图。",
        "focus": ["RTOS 能力边界", "POSIX 风格接口", "与其他 RTOS 的差异"],
        "seealso": ["wiki/concepts/实时操作系统.md", "wiki/entities/freertos.md", "wiki/entities/threadx.md"],
    },
    "wiki/entities/dds.md": {
        "title": "DDS",
        "aliases": ["Data Distribution Service", "RTPS", "DDS Middleware"],
        "tags": ["entity", "DDS", "中间件"],
        "sources": ["中间件/DDS/分布式实时通信—DDS概述.md", "中间件/DDS/分布式实时通信—DDS进阶.md"],
        "summary": "DDS 是实时分布式通信领域的重要中间件对象，当前知识库已经覆盖概述和进阶两层资料。",
        "focus": ["发布订阅模型", "实时分布式通信", "QoS 与系统解耦"],
        "seealso": ["wiki/concepts/ipc.md", "wiki/concepts/rpc.md"],
    },
    "wiki/entities/u-boot.md": {
        "title": "U-Boot",
        "aliases": ["Uboot", "Bootloader", "Das U-Boot"],
        "tags": ["entity", "U-Boot", "bootloader"],
        "sources": ["Linux/uboot+Linux_Kernel启动/uboot/超详细分析Bootloader（Uboot）到内核的启动流程（万字长文！）.md", "Linux/uboot+Linux_Kernel启动/uboot/【ARM】Uboot代码分析-阿里云开发者社区.md"],
        "summary": "U-Boot 是启动链路中的关键对象，当前知识库已经具备从 Bootloader 到内核切换路径的材料。",
        "focus": ["Bootloader 阶段职责", "向内核传递启动参数", "与 Linux kernel 启动的衔接"],
        "seealso": ["wiki/concepts/启动流程.md", "wiki/entities/linux.md"],
    },
}

CONCEPT_PAGES = {
    "wiki/concepts/中断.md": {
        "title": "中断",
        "aliases": ["Interrupt", "IRQ", "异常与中断"],
        "tags": ["concept", "中断", "IRQ"],
        "sources": ["Linux/中断/Linux内核中的软中断、tasklet和工作队列详解.md", "ARM/架构/异常和中断处理.md", "ARM/GIC/GIC.md", "RiscV/中断/plic_clint.md"],
        "summary": "中断是当前知识库跨 Linux、ARM 与 RISC-V 的公共基础概念，涉及异常类型、控制器架构和内核处理路径。",
        "questions": ["不同架构下的中断源和控制器模型有何差异", "Linux 内核如何承接硬中断与软中断", "GIC、PLIC/CLINT 在系统中的职责如何划分"],
        "related": ["wiki/entities/linux.md", "wiki/entities/arm.md", "wiki/entities/risc-v.md", "wiki/concepts/gic.md"],
    },
    "wiki/concepts/gic.md": {
        "title": "GIC",
        "aliases": ["Generic Interrupt Controller", "ARM GIC"],
        "tags": ["concept", "GIC", "ARM"],
        "sources": ["ARM/GIC/GIC.md", "ARM/GIC/GIC600/gic_600.md"],
        "summary": "GIC 是 ARM 平台里的核心中断控制架构，当前知识库涵盖版本差异、中断类型、状态转换和 GIC-600 相关资料。",
        "questions": ["各版本 GIC 的结构差异是什么", "SGI/PPI/SPI/LPI 在系统中的边界如何理解", "GIC 初始化与 Linux irq_domain 的关系是什么"],
        "related": ["wiki/entities/arm.md", "wiki/concepts/中断.md"],
    },
    "wiki/concepts/设备树.md": {
        "title": "设备树",
        "aliases": ["Device Tree", "DT", "DTS"],
        "tags": ["concept", "设备树", "DTS"],
        "sources": ["Linux/驱动/DTS/Device Tree：基本概念.md", "Linux/驱动/DTS/Linux设备树--设备树格式和使用.md", "Linux/驱动/DTS/Linux 设备树语法（.dts）及如何从设备树获取节点信息.md"],
        "summary": "设备树是嵌入式 Linux 中描述硬件拓扑和驱动绑定关系的核心机制，当前知识库已经积累概念、语法和使用路径。",
        "questions": ["设备树如何描述硬件资源与层级关系", "DTS/DTB/overlay 在工程实践中如何协作", "驱动如何从设备树节点解析配置"],
        "related": ["wiki/entities/linux.md", "wiki/concepts/驱动模型.md"],
    },
    "wiki/concepts/进程调度.md": {
        "title": "进程调度",
        "aliases": ["Process Scheduling", "Linux scheduler", "CFS"],
        "tags": ["concept", "进程调度", "CFS"],
        "sources": ["Linux/进程调度/linux进程调度.md", "Linux/进程调度/Linux CFS 调度器：原理、设计与内核实现（2023）.md", "Linux/进程调度/深入理解Linux内核进程的管理与调度(最详细).md"],
        "summary": "进程调度是理解 Linux 运行时行为的关键主题，当前知识库已覆盖上下文切换、CFS 和调度器设计。",
        "questions": ["上下文切换的代价和关键路径是什么", "CFS 的核心数据结构和公平性机制是什么", "如何把调度行为和性能现象关联起来"],
        "related": ["wiki/entities/linux.md"],
    },
    "wiki/concepts/内存管理.md": {
        "title": "内存管理",
        "aliases": ["Memory Management", "MM", "mmap", "NUMA"],
        "tags": ["concept", "内存管理", "MM"],
        "sources": ["Linux/内存管理/内存管理总结.md", "Linux/内存管理/Linux内存管理初始化.md", "Linux/内存管理/细说mmap系统调用.md", "Linux/内存管理/NUMA 架构.md"],
        "summary": "内存管理是 Linux 知识分支中的高密度主题，当前资料覆盖初始化、分配、虚拟内存与 NUMA。",
        "questions": ["内核启动阶段如何完成内存初始化", "kmalloc、vmalloc、mmap 适用于哪些场景", "NUMA 对性能与分配策略的影响是什么"],
        "related": ["wiki/entities/linux.md"],
    },
    "wiki/concepts/usb.md": {
        "title": "USB",
        "aliases": ["USB protocol", "通用串行总线", "USB 2.0"],
        "tags": ["concept", "USB", "协议"],
        "sources": ["硬件接口/USB/USB协议.md", "硬件接口/USB/USB描述符.md", "硬件接口/USB/USB枚举.md", "硬件接口/USB/usb驱动.md"],
        "summary": "USB 是当前接口类资料里最完整的一条主线，已经覆盖协议、描述符、枚举和驱动视角。",
        "questions": ["USB 协议栈从物理层到枚举流程如何串联", "描述符如何决定主机识别和驱动绑定", "协议理解如何映射到 Linux 驱动实现"],
        "related": ["wiki/entities/linux.md", "wiki/concepts/驱动模型.md"],
    },
    "wiki/concepts/pcie.md": {
        "title": "PCIe",
        "aliases": ["PCI Express", "Root Complex", "Endpoint"],
        "tags": ["concept", "PCIe", "总线"],
        "sources": ["硬件接口/PCIe/PCIe.md", "硬件接口/PCIe/Linux PCIe源码解析.md"],
        "summary": "PCIe 是当前高速总线主题的主入口，内容从基础概念延伸到配置空间、协议层和 Linux 驱动框架。",
        "questions": ["RC 与 EP 的边界和职责是什么", "PCIe 协议层如何和 Linux 驱动模型衔接", "设备树在 PCIe 初始化中扮演什么角色"],
        "related": ["wiki/entities/linux.md", "wiki/concepts/设备树.md"],
    },
    "wiki/concepts/ipc.md": {
        "title": "IPC",
        "aliases": ["Inter Process Communication", "进程间通信", "消息通信"],
        "tags": ["concept", "IPC", "中间件"],
        "sources": ["中间件/QNX/IPC.md", "中间件/RPC/分布式通信技术之远程调用：RPC.md", "中间件/OpenAMP/OpenAMP.md", "中间件/RpMSG/RpMSG Lite.md"],
        "summary": "IPC 在当前知识库里跨本地 OS 通信、分布式调用和异构多核消息传递三类场景。",
        "questions": ["本地 IPC 与分布式 RPC 的抽象边界是什么", "OpenAMP/RPMsg 如何解决异构核间通信", "不同 IPC 模型各自适合怎样的实时性与解耦需求"],
        "related": ["wiki/entities/openamp.md"],
    },
    "wiki/concepts/驱动模型.md": {
        "title": "驱动模型",
        "aliases": ["Driver Model", "设备驱动", "Platform Device", "Device Model"],
        "tags": ["concept", "驱动模型", "Linux"],
        "sources": ["Linux/驱动/linux平台设备驱动架构详解 Linux Platform Device and Driver.md", "Linux/驱动/Linux驱动常用API整理.md", "Linux/驱动/【原创】linux设备模型之kset_kobj_ktype分析.md"],
        "summary": "驱动模型是 Linux 内核与硬件交互的组织骨架，当前资料覆盖平台设备、设备模型对象和常用驱动 API。",
        "questions": ["platform bus 在驱动框架中的定位是什么", "kobject、kset、ktype 如何组织设备模型", "驱动 API 与设备树如何协同完成设备初始化"],
        "related": ["wiki/entities/linux.md", "wiki/concepts/设备树.md", "wiki/concepts/usb.md"],
    },
    "wiki/concepts/启动流程.md": {
        "title": "启动流程",
        "aliases": ["Boot Flow", "Boot Process", "系统启动"],
        "tags": ["concept", "启动", "boot"],
        "sources": ["Linux/uboot+Linux_Kernel启动/Linux_kernel启动/Linux内核启动流程.md", "Linux/uboot+Linux_Kernel启动/Linux_kernel启动/start_kernel介绍.md", "Linux/uboot+Linux_Kernel启动/Linux_kernel启动/start_kernel详解系列之【setup_arch】.md", "Linux/uboot+Linux_Kernel启动/uboot/超详细分析Bootloader（Uboot）到内核的启动流程（万字长文！）.md"],
        "summary": "启动流程把 Bootloader、内核入口、早期初始化和用户态拉通，是当前 Linux 系统理解链路中的重要主线。",
        "questions": ["Bootloader 到内核的控制权是如何切换的", "start_kernel 之前和之后分别完成了哪些初始化", "启动优化通常应该从哪几个阶段切入"],
        "related": ["wiki/entities/u-boot.md", "wiki/entities/linux.md"],
    },
    "wiki/concepts/调试工具.md": {
        "title": "调试工具",
        "aliases": ["Debugging Tools", "调试方法", "Observability"],
        "tags": ["concept", "调试", "工具"],
        "sources": ["Linux/调试/Linux调试工具.md", "Linux/Vmware+gdb调试Linux内核.md", "Trace32/调试工具-Trace32.md"],
        "summary": "调试工具这条线连接了 Linux 用户态/内核态调试和芯片级调试，是把现象定位到根因的关键方法集合。",
        "questions": ["Linux 层调试和芯片级调试各自适合什么场景", "gdb、perf、ftrace、Trace32 如何形成协同链路", "面对启动期或驱动期问题应优先选择什么观察手段"],
        "related": ["wiki/entities/linux.md", "wiki/entities/trace32.md", "wiki/concepts/启动流程.md"],
    },
    "wiki/concepts/rpc.md": {
        "title": "RPC",
        "aliases": ["Remote Procedure Call", "远程调用"],
        "tags": ["concept", "RPC", "通信"],
        "sources": ["中间件/RPC/分布式通信技术之远程调用：RPC.md", "中间件/DDS/分布式实时通信—DDS概述.md"],
        "summary": "RPC 是分布式通信里最经典的抽象之一，适合和本地 IPC、DDS 这类消息模型一起对照理解。",
        "questions": ["RPC 如何隐藏网络边界并暴露调用语义", "RPC 与消息队列、发布订阅相比各自适合什么场景", "分布式系统里 RPC 的性能与可靠性代价是什么"],
        "related": ["wiki/concepts/ipc.md", "wiki/entities/dds.md"],
    },
    "wiki/concepts/实时操作系统.md": {
        "title": "实时操作系统",
        "aliases": ["RTOS", "Real-Time Operating System"],
        "tags": ["concept", "RTOS", "实时系统"],
        "sources": ["RTOS/FreeRTOS/Freertos使用.md", "RTOS/ThreadX/ThreadX文档.md", "RTOS/NuttX/NuttX简介.md", "RTOS/Freertos和Threadx.md", "中间件/QNX/IPC.md"],
        "summary": "实时操作系统是嵌入式系统的关键主线，当前知识库已经形成 FreeRTOS、ThreadX、NuttX 和 QNX 的对照素材。",
        "questions": ["不同 RTOS 的调度模型和资源模型有何差异", "RTOS 与 Linux 在实时性和系统复杂度之间如何取舍", "不同场景下该如何选择 FreeRTOS、ThreadX、NuttX 或 QNX"],
        "related": ["wiki/entities/freertos.md", "wiki/entities/threadx.md", "wiki/entities/nuttx.md", "wiki/entities/qnx.md"],
    },
    "wiki/concepts/i2c.md": {
        "title": "I2C",
        "aliases": ["Inter-Integrated Circuit", "I2C bus"],
        "tags": ["concept", "I2C", "总线"],
        "sources": ["硬件接口/I2C/I2C总线.md", "Linux/驱动/I2C/i2c驱动.md"],
        "summary": "I2C 是嵌入式系统里最基础也最常见的低速串行总线之一，当前知识库已经兼顾协议与 Linux 驱动视角。",
        "questions": ["I2C 总线的时序和主从机制如何工作", "协议理解如何落到 Linux I2C 驱动模型上", "I2C 在系统设计里通常承担哪些设备连接职责"],
        "related": ["wiki/entities/linux.md", "wiki/concepts/驱动模型.md"],
    },
    "wiki/concepts/can.md": {
        "title": "CAN",
        "aliases": ["Controller Area Network", "CAN bus"],
        "tags": ["concept", "CAN", "总线"],
        "sources": ["硬件接口/CAN/CAN协议.md"],
        "summary": "CAN 是工业与汽车电子场景中极高频的总线协议，当前知识库已经有协议结构和帧格式相关入口。",
        "questions": ["CAN 的帧格式、仲裁机制和错误处理如何协作", "为什么 CAN 在汽车和工业场景里长期稳定存在", "理解协议之后，系统集成时通常还要关注哪些工程问题"],
        "related": ["wiki/entities/autosar.md"],
    },
}

WIKI_PAGE_TITLES = {
    **{path: data["title"] for path, data in ENTITY_PAGES.items()},
    **{path: data["title"] for path, data in CONCEPT_PAGES.items()},
}


def merge_unique(existing, new_values):
    items = list(existing) if isinstance(existing, list) else []
    for value in new_values:
        if value not in items:
            items.append(value)
    return items


def update_seed_note(path: Path, root: Path, config: dict) -> None:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    title = str(meta.get("title", "")).strip() or title_from_body(body, path)
    meta["title"] = title
    meta["type"] = str(meta.get("type", "")).strip() or "note"
    meta["status"] = "active"
    meta["aliases"] = merge_unique(meta.get("aliases", []), config.get("aliases", []))
    meta["sources"] = merge_unique(meta.get("sources", []), config.get("sources", []))
    meta["tags"] = merge_unique(meta.get("tags", []), config.get("tags", []))
    meta["updated_at"] = TODAY
    rendered = dump_frontmatter(meta) + "\n" + ensure_h1(body, title).strip("\n") + "\n"
    path.write_text(rendered, encoding="utf-8")


def md_link(from_path: Path, target: str) -> str:
    source_dir = from_path.parent.as_posix()
    target_path = Path(target).as_posix()
    label = WIKI_PAGE_TITLES.get(target, Path(target).stem)
    rel = relpath(target_path, source_dir or ".")
    return f"[{label}]({rel})"


def wikilink_label(target: str) -> str:
    return WIKI_PAGE_TITLES.get(target, Path(target).stem)


def render_seed_page(page_path: Path, page_type: str, data: dict) -> str:
    meta = {
        "title": data["title"],
        "type": page_type,
        "status": "active",
        "tags": data["tags"],
        "aliases": data["aliases"],
        "sources": data["sources"],
        "updated_at": TODAY,
    }
    lines = [dump_frontmatter(meta), f"# {data['title']}", "", data["summary"], ""]

    if "focus" in data:
        lines.extend(["## 当前关注", ""])
        for item in data["focus"]:
            lines.append(f"- {item}")
        lines.append("")

    if "questions" in data:
        lines.extend(["## 核心问题", ""])
        for item in data["questions"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## 相关资料", ""])
    for item in data["sources"]:
        lines.append(f"- {md_link(page_path, item)}")
    lines.append("")

    related = data.get("seealso", []) or data.get("related", [])
    if related:
        lines.extend(["## 主题连接", ""])
        for item in related:
            lines.append(f"- [[{wikilink_label(item)}]]")
        lines.append("")

    lines.extend(["## 延伸链接", ""])
    for item in related:
        lines.append(f"- {md_link(page_path, item)}")
    lines.append("")
    return "\n".join(lines)


def write_seed_page(path: Path, page_type: str, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_seed_page(path, page_type, data), encoding="utf-8")


def build_readme() -> str:
    meta = {
        "title": "个人知识库",
        "type": "hub",
        "status": "active",
        "tags": ["knowledge-base", "wiki", "hub"],
        "aliases": ["Personal Knowledge Base", "PKB", "知识库首页"],
        "sources": ["purpose.md", "schema.md", "wiki/index.md"],
        "updated_at": TODAY,
    }
    lines = [
        dump_frontmatter(meta),
        "# 个人知识库",
        "",
        "这个仓库正在从“按目录存放资料”升级为“可搜索、可关联、可持续维护”的个人知识库。",
        "",
        "## 快速入口",
        "",
        "- [知识库目标](purpose.md)",
        "- [知识库规范](schema.md)",
        "- [Wiki 入口](wiki/index.md)",
        "- [Wiki 总览](wiki/overview.md)",
        "- [仓库索引](docs/REPO_INDEX.md)",
        "- [搜索页面](docs/search.html)",
        "",
        "## 首批主题地图",
        "",
        "### 核心实体",
        "",
        "- [Linux](wiki/entities/linux.md)",
        "- [ARM](wiki/entities/arm.md)",
        "- [RISC-V](wiki/entities/risc-v.md)",
        "- [FreeRTOS](wiki/entities/freertos.md)",
        "- [ThreadX](wiki/entities/threadx.md)",
        "- [Buildroot](wiki/entities/buildroot.md)",
        "- [OpenAMP](wiki/entities/openamp.md)",
        "- [AUTOSAR](wiki/entities/autosar.md)",
        "- [Trace32](wiki/entities/trace32.md)",
        "- [QNX](wiki/entities/qnx.md)",
        "- [NuttX](wiki/entities/nuttx.md)",
        "- [DDS](wiki/entities/dds.md)",
        "- [U-Boot](wiki/entities/u-boot.md)",
        "",
        "### 核心概念",
        "",
        "- [中断](wiki/concepts/中断.md)",
        "- [GIC](wiki/concepts/gic.md)",
        "- [设备树](wiki/concepts/设备树.md)",
        "- [进程调度](wiki/concepts/进程调度.md)",
        "- [内存管理](wiki/concepts/内存管理.md)",
        "- [USB](wiki/concepts/usb.md)",
        "- [PCIe](wiki/concepts/pcie.md)",
        "- [IPC](wiki/concepts/ipc.md)",
        "- [驱动模型](wiki/concepts/驱动模型.md)",
        "- [启动流程](wiki/concepts/启动流程.md)",
        "- [调试工具](wiki/concepts/调试工具.md)",
        "- [RPC](wiki/concepts/rpc.md)",
        "- [实时操作系统](wiki/concepts/实时操作系统.md)",
        "- [I2C](wiki/concepts/i2c.md)",
        "- [CAN](wiki/concepts/can.md)",
        "",
        "## 当前内容范围",
        "",
        "- Linux、RTOS、ARM、RISC-V",
        "- 硬件接口与芯片基础设施",
        "- 中间件、验证工具、调试工具",
        "- 工作中沉淀的实践笔记与问题总结",
        "",
        "## 维护方式",
        "",
        "- 现有 Markdown 已统一纳入 frontmatter 规范。",
        "- `docs/search.html` 基于标题、路径、标签和别名提供静态搜索。",
        "- `wiki/` 目录承载逐步提炼出来的实体页、概念页和高价值问答。",
        "",
        "## 下一阶段",
        "",
        "- 扩展第二批实体页和概念页，补更多 `aliases` / `sources`。",
        "- 逐步引入 `[[wikilink]]`、反向链接和主题聚合页。",
        "- 基于现有 frontmatter 与索引，继续增强自动问答和知识图谱能力。",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    for rel, config in SEED_NOTES.items():
        update_seed_note(root / rel, root, config)

    for rel, data in ENTITY_PAGES.items():
        write_seed_page(root / rel, "entity", data)

    for rel, data in CONCEPT_PAGES.items():
        write_seed_page(root / rel, "concept", data)

    (root / "README.md").write_text(build_readme(), encoding="utf-8")

    print(
        f"Updated {len(SEED_NOTES)} seed notes, "
        f"generated {len(ENTITY_PAGES)} entity pages and {len(CONCEPT_PAGES)} concept pages"
    )


if __name__ == "__main__":
    main()
