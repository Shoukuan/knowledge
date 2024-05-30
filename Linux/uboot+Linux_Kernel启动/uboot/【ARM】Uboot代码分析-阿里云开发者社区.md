# 【ARM】Uboot代码分析-阿里云开发者社区

[【ARM】Uboot代码分析-阿里云开发者社区](https://developer.aliyun.com/article/23878)

![Uboot启动](Uboot启动.png)

## UBoot启动过程

UBoot其启动过程主要可以分为两个部分，Stage1和Stage2 。其中Stage1是用汇编语言实现的，主要完成硬件资源的初始化。而Stage2则是用C语言实现。主要完成内核程序的调用。这两个部分的主要执行流程如下：

**stage1包含以下步骤：**

1. 硬件设备初始化

2. 为加载stage2准备RAM空间

3. 拷贝stage2的代码到RAM空间

4. 设置好堆栈

5. 跳转到stage2的C语言入口点

**stage2一般包括以下步骤：**

1. 初始化本阶段要使用的硬件设备

2. 检测系统内存映射

3. 将kernel映射和根文件系统映射从Flash读到RAM空间中

4. 为内核设置启动参数

5. 调用内核
