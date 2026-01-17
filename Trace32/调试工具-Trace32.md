# 调试工具（三）：trace32
<!-- TOC -->

- [Peripheral Files Programming](#peripheral-files-programming)
- [1. TPIU (Trace Port Interface Unit)](#1-tpiu-trace-port-interface-unit)
- [2. ETM (Embedded Trace Macrocell)](#2-etm-embedded-trace-macrocell)
- [3. STM (System Trace Macrocell)](#3-stm-system-trace-macrocell)
- [在 Trace32 中的使用场景](#-trace32-)

<!-- TOC END -->


[调试工具（三）：trace32](https://www.dumpstack.cn/index.php/2022/02/25/398.html#37)

## Peripheral Files Programming

![Per文件参考](Per文件参考.jpg)
图中数字后的点表示是十进制
![GROUP关键字](GROUP关键字.jpg)

**HGROUP**: Define read-once/write GROUP
**RGROUP**: Define read-only GROUP
**WSGROUP**: Define write-only and shadow GROUP
**WGROUP**: Define write-only GROUP
**SGROUP**: Define sequence GROUP

**BITFLD**: bit
**HEXMASK**: Define bits for a hexadecimal display

**对齐**:AUTOINDENT.ON  LEFT/RIGHT/CENTER TREE/LINE

**BUTTON**: Define command button
**HIDE**: Define write-only line

per文件参数传递：

xxx.per AZNC:0x002D000000
per文件中：
ENTRY &TOP_CRU_Base=0x002D000000

BASE &TOP_CRU_Base

cmm中函数声明调用：

GOSUB fun_name "&input_param"
RETURNVALUES &out_value

fun_name
(
  PRIVATE &function_value
  PARAMETERS &input_param

  //add function

  RETURN "&function_value"
)

[Trace32内存访问](https://www.cnblogs.com/arnoldlu/p/17428690.html)

![单个Acess_Class描述](单个Acess_Class描述.png)
![单个Acess_Class描述1](单个Acess_Class描述1.png)
![单个Acess_Class描述2](单个Acess_Class描述2.png)

内存访问主体包含CPU、MMU，Cache三个。常见访问组合：
![常见访问组合](常见访问组合.png)

## 1. TPIU (Trace Port Interface Unit)

作用：
TPIU 是 ARM 架构中用于管理跟踪数据输出的硬件模块，负责将芯片内部的跟踪数据格式化并通过物理接口（如并行或串行端口）传输到外部调试工具（如 Trace32 的跟踪捕获设备）。
数据类型：
TPIU 本身不生成数据，而是作为“管道”传输其他跟踪模块（如 ETM 或 STM）生成的跟踪数据流。
传输的数据格式包括：时间戳、同步标记、时钟控制信号等。
支持多种接口协议（如 SWO (Serial Wire Output) 或并行跟踪端口）。
典型应用：
配置 TPIU 的时钟频率、数据宽度和输出模式，确保跟踪数据能稳定传输到 Trace32 工具。

## 2. ETM (Embedded Trace Macrocell)

作用：
ETM 是 ARM 处理器中用于实时指令跟踪的硬件模块，记录 CPU 核心的程序执行流程（如指令地址、分支跳转、异常/中断等）。
数据类型：
ETM 生成指令级跟踪数据，包括：
程序计数器（PC）的实时变化。
分支跳转、函数调用/返回的路径。
异常/中断触发的上下文切换。
数据访问（可选配置，但主要侧重于指令流）。
典型应用：
用于分析代码执行效率、死锁、崩溃现场重建等需要精确指令流回溯的场景。

## 3. STM (System Trace Macrocell)

作用：
STM 是用于系统级跟踪的硬件模块，记录芯片内部总线、外设、多核间交互等系统级事件。
数据类型：
STM 生成系统事件跟踪数据，包括：
总线事务（如 AXI/AHB 总线上的读写操作）。
外设状态变化（如 GPIO、DMA、定时器等）。
多核间通信（如核间中断、共享资源访问）。
用户自定义事件（通过软件插桩生成）。
典型应用：
诊断系统级问题（如总线争用、外设配置错误、多核同步问题）。
关键区别总结
模块  | 数据来源 | 数据类型 | 典型用途
TPIU 传输管道 原始数据流（无内容） 将 ETM/STM 数据传输出芯片
ETM CPU 核心指令流 指令执行轨迹 代码级调试、崩溃分析
STM 系统总线和外设 系统事件、总线活动 系统级性能分析、外设调试

## 在 Trace32 中的使用场景

ETM 数据：通过 Trace32 的指令跟踪功能（如 ETMVIEW）可视化程序执行路径。  
STM 数据：使用 Trace32 的系统跟踪工具（如 STREAM 或 SYSTEMVIEW）分析总线活动或外设行为。  
TPIU 配置：需在 Trace32 中设置时钟、触发条件和数据捕获方式（如 SYStem.Option.TPIUClock）。  

