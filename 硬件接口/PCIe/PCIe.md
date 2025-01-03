# PCIe

## [PCIe（一） —— 基础概念与设备树](https://r12f.com/posts/pcie-1-basics/#PCIe%E6%80%BB%E4%BD%93%E6%A1%86%E5%9B%BE)

## [PCIe（二） —— 配置空间](https://r12f.com/posts/pcie-2-config/)

## [PCIe（三）—— PCIe协议栈，事务层和数据链路层](https://r12f.com/posts/pcie-3-tl-dll/)

## [PCIe（四）—— 物理层](https://r12f.com/posts/pcie-4-phy/)

## PCIe RC&EP

在 PCIe（Peripheral Component Interconnect Express）体系中，RC（Root Complex）和 EP（Endpoint）是两种关键的设备类型。RC 和 EP 的配置决定了 PCIe 链路的建立和设备间通信的实现。

### 1. RC 和 EP 的作用

Root Complex (RC)

是 PCIe 拓扑的起点，与处理器和内存直接连接。
功能：
负责初始化 PCIe 链路。
构建并管理 PCIe 总线和设备拓扑（枚举、资源分配）。
执行配置空间访问，控制链路上的 Endpoint 设备。
Endpoint (EP)

是 PCIe 总线的终点设备，例如网络卡、显卡、NVMe 固态硬盘等。
功能：
作为数据的消费者或生产者，响应 Root Complex 的配置请求。
通过 DMA 或直接 I/O 完成与主存的交互。

### 2. RC 和 EP 的硬件配置

(1) RC 的硬件配置
RC 是一个特殊的 PCIe设备，通常内嵌于主板芯片组中（如 Intel 的 PCH 或 AMD 的 SoC）。
配置阶段完成以下任务：
PCIe链路初始化：
通过 Link Training and Status State Machine (LTSSM) 确保链路正常工作。
配置空间访问：
使用标准 PCIe 配置访问方法，读取和写入配置空间。
分配总线号：
为下游设备分配总线号、设备号和功能号 (BDF)。
资源分配：
根据设备需求分配内存和 I/O 地址空间，写入设备的 Base Address Registers (BARs)。
中断配置：
配置中断机制（Legacy、MSI 或 MSI-X）。
(2) EP 的硬件配置
EP 是独立的 PCIe 设备，需要完成以下硬件配置：
配置空间实现：
必须实现标准 PCIe 配置空间，并支持 Vendor ID、Device ID 等字段。
支持 BAR，用于声明设备的资源需求。
DMA引擎配置：
通常内置 DMA 引擎，用于高效的数据传输。
中断机制实现：
支持 PCIe 标准中断（如 MSI 或 MSI-X），便于与 RC 通信。
协议层实现：
处理 TLP (Transaction Layer Packet) 和 DLLP (Data Link Layer Packet)。

### 3. 软件配置流程

(1) RC 配置过程
Root Complex 的配置流程通常由操作系统或固件完成，以下是关键步骤：

枚举设备：

扫描所有下游设备，通过读取配置空间的 Vendor ID 和 Device ID 确定设备存在。
分配资源：

为设备分配内存和 I/O地址空间，将分配结果写入 BAR。
配置中断：

配置设备的中断方式（如启用 MSI/MSI-X），并将中断号写入设备。
加载驱动程序：

根据设备的 Vendor ID 和 Device ID，加载适配的设备驱动程序。
(2) EP 配置过程
Endpoint 的配置通常由设备固件和驱动程序共同完成。以下是典型流程：

上电初始化：

Endpoint 的内部控制器初始化配置空间，包括设置 Vendor ID、Device ID 和 BAR。
链路训练：

等待 RC 发起链路训练，确保 PCIe 链路正常工作。
响应配置请求：

当 RC 访问 EP 的配置空间时，EP 的硬件逻辑会提供相应的配置数据。
驱动加载和初始化：

驱动程序完成对设备的初始化，如配置 DMA 引擎、中断向量等。

### 4. 配置空间字段解析

(1) 标准 PCIe 配置空间
PCIe 设备的配置空间大小为 256B（支持扩展到 4KB），主要字段如下：

偏移地址 字段名 描述
0x00 Vendor ID 供应商标识符
0x02 Device ID 设备标识符
0x04 Command 启用设备功能（如 I/O、内存访问等）
0x10-0x24 BAR0-BAR5 基址寄存器，声明设备资源需求
0x3C Interrupt Line 中断线号
(2) 扩展能力
支持 MSI、MSI-X、热插拔等高级功能的设备会在配置空间中包含扩展能力字段。

### 5. 驱动程序实现中的区别

(1) RC 驱动程序
功能：配置和管理 PCIe 链路上的所有设备。
关键任务：
调用 pci_register_driver 注册驱动。
扫描和初始化 PCIe 设备。
配置设备的 BAR 和中断。
(2) EP 驱动程序
功能：实现设备功能并与 RC 通信。
关键任务：
初始化设备配置空间。
配置 DMA 引擎。
处理 RC 发来的 TLP 请求。

### 6. RC 和 EP 配置的交互

RC 发起配置访问

RC 通过配置 TLP 读取/写入 EP 的配置空间。
EP 根据请求类型提供相应响应。
EP 声明资源

EP 在其配置空间的 BAR 中声明需要的资源大小。
RC 根据系统资源分配，写入具体的物理地址到 BAR。
链路中断配置

RC 和 EP 协调配置中断向量，用于完成数据传输的同步。

### 7. 调试工具

lspci：查看 RC 和 EP 的配置。
pcitree：图形化显示 PCIe 设备树。
setpci：手动修改 PCI 配置空间。
通过 RC 和 EP 的正确配置，可以完成 PCIe 链路的建立，并实现设备功能的启用和数据传输的高效管理。

RC和EP分别配置的寄存器
在 PCIe 系统中，RC (Root Complex) 和 EP (Endpoint) 都需要初始化和配置多个寄存器以建立通信和进行数据传输。以下是两者分别需要配置的寄存器详细说明：

1. Root Complex (RC) 配置寄存器
(1) 配置空间寄存器
RC 的配置空间寄存器主要用于初始化和管理 PCIe 总线上的设备。以下是关键寄存器：

寄存器名称 地址偏移 描述
Command 0x04 启用内存空间访问、I/O空间访问和总线主设备功能等。
Status 0x06 设备状态标志，例如是否有中断挂起、是否发生错误等。
Base Address Registers (BARs) 0x10-0x24 用于声明设备资源需求（如内存或 I/O 地址范围）。RC 不直接分配，但会根据设备的 BAR 请求分配具体地址。
Bus Number 0x18 分配的总线号（Primary Bus Number、Secondary Bus Number 和 Subordinate Bus Number）。
Interrupt Line 0x3C 指定设备的中断线号，用于中断管理。
(2) RC 内部寄存器
RC 除了标准 PCI 配置空间外，还包含专用寄存器，用于管理 PCIe 链路和总线功能。

寄存器名称 描述
Link Control and Status 控制 PCIe 链路的启用和状态监控，包括链路速度和宽度。
Root Control 控制 RC 的全局功能，例如中断路由、错误报告等。
Root Status 显示与 RC 相关的错误和中断状态信息。
Error Reporting 用于高级错误报告 (Advanced Error Reporting, AER) 的寄存器，用于检测和记录链路层和事务层错误。
MSI/MSI-X Control 配置 MSI 或 MSI-X 中断。
(3) DMA 和中断配置寄存器
这些寄存器用于配置 RC 发起 DMA 传输和中断机制。

寄存器名称 描述
DMA Control 控制 DMA 引擎的启动、停止以及传输模式配置。
DMA Status 显示 DMA 传输的状态，例如完成或错误。
Interrupt Controller 管理设备中断路由到主处理器，包括 MSI 和 Legacy 中断管理。
2. Endpoint (EP) 配置寄存器
(1) 配置空间寄存器
EP 的配置空间寄存器是标准 PCI 配置的一部分，必须实现以下字段：

寄存器名称 地址偏移 描述
Vendor ID 0x00 指定供应商标识符，由 PCI-SIG 分配。
Device ID 0x02 指定设备标识符，由设备供应商分配。
Command 0x04 启用内存访问、I/O 访问和总线主功能。
Status 0x06 指示设备的当前状态，例如错误和中断挂起。
BAR (Base Address Registers) 0x10-0x24 声明设备需要的内存空间或 I/O 空间，RC 根据 BAR 的请求分配实际地址。
Subsystem ID 0x2C 子系统标识符，用于区分不同的设备功能。
Capabilities Pointer 0x34 指向扩展功能的能力结构列表，例如 MSI/MSI-X 或 AER。
(2) 扩展能力寄存器
支持高级功能的设备必须实现扩展能力寄存器，例如：

寄存器名称 描述
MSI/MSI-X Capability 支持 Message Signaled Interrupts (MSI/MSI-X) 的中断配置，包括中断向量数量和中断状态。
Power Management 支持电源管理功能，包括设备低功耗模式的状态控制。
PCIe Capability 包含 PCIe 特有的功能，例如链路状态、链路宽度和速度等。
Advanced Error Reporting 包含错误检测和报告功能，用于记录链路和事务层的错误。
(3) 内部专用寄存器
Endpoint 设备的具体功能由厂商定义，可能包括以下寄存器：

寄存器名称 描述
DMA Engine Registers 控制 DMA 的源地址、目标地址、传输长度和传输状态。
Interrupt Control 管理中断配置，例如启用 MSI/MSI-X 中断。
Configuration Control 控制设备内部逻辑的初始化，例如 PHY 层设置、链路宽度设置等。
3. RC 和 EP 配置交互
链路建立

RC 启动链路训练，通过 LTSSM 状态机完成链路初始化，确保 RC 和 EP 能够正常通信。
资源分配

RC 读取 EP 的 BAR 配置，分配内存或 I/O 地址空间，并将分配的物理地址写入 EP 的 BAR。
中断配置

RC 配置 EP 的 MSI 或 MSI-X 中断，确保 EP 能够通过中断通知 RC。
DMA 设置

RC 或 EP 配置 DMA 控制寄存器，启用数据传输。
事务管理

RC 发起配置请求（Configuration TLP），EP 响应请求并完成相关配置。
通过对 RC 和 EP 的寄存器配置，可以实现 PCIe 链路的初始化、资源分配以及设备间高效的数据传输。
