# Fastboot

Fastboot 是一种用于 Android 设备的协议，允许用户通过 USB 连接与设备进行通信，执行各种操作，如刷入系统镜像、解锁引导加载程序等。以下是 Fastboot 的基本概念和操作流程。  

## 基本概念

- **Fastboot 协议**：一种基于 USB 的协议，用于与 Android 设备进行通信。
- **Fastboot 模式**：设备在 Fastboot 模式下可以接收命令并执行操作，如刷入系统镜像、解锁引导加载程序等。
- **Fastboot 命令**：一组用于与设备交互的命令，如 `flash`、`boot`、`reboot` 等。

## Fastboot 操作流程

1. **进入 Fastboot 模式**：通常通过按住特定的按键组合（如音量下键 + 电源键）来进入 Fastboot 模式。
2. **连接设备**：将设备通过 USB 线连接到计算机，并确保计算机上安装了 Fastboot 工具。
3. **打开终端**：在计算机上打开终端或命令提示符窗口。
4. **检查设备连接**：使用命令 `fastboot devices` 检查设备是否已连接并识别。如果设备正确连接，终端将显示设备的序列号。
5. **执行 Fastboot 命令**：使用 Fastboot 命令与设备交互。例如：
   - `fastboot flash boot boot.img`：刷入引导镜像。
   - `fastboot flash system system.img`：刷入系统镜像。
   - `fastboot reboot`：重启设备。
6. **退出 Fastboot 模式**：完成操作后，可以使用 `fastboot reboot` 命令重启设备，或手动断开 USB 连接并重启设备。

## Fastboot 命令示例

```bash
# 检查设备连接
fastboot devices
# 刷入引导镜像
fastboot flash boot boot.img
# 刷入系统镜像
fastboot flash system system.img
# 重启设备
fastboot reboot
# 解锁引导加载程序
fastboot oem unlock
# 锁定引导加载程序
fastboot oem lock
# 查看设备信息
fastboot getvar all
# 刷入恢复镜像
fastboot flash recovery recovery.img
# 刷入用户数据分区
fastboot flash userdata userdata.img
# 刷入分区表
fastboot flash partition gpt.bin
# 刷入特定分区
fastboot flash <partition_name> <image_file>
# 清除缓存分区
fastboot erase cache
# 清除用户数据分区
fastboot erase userdata
# 清除系统分区
fastboot erase system
# 清除引导分区
fastboot erase boot
# 清除恢复分区
fastboot erase recovery
# 刷入分区表
fastboot flash partition gpt.bin
# 刷入特定分区
fastboot flash <partition_name> <image_file>
# 刷入多个分区
fastboot flash boot boot.img system system.img recovery recovery.img
# 刷入多个分区（使用分区表）
fastboot flashall -w
# 刷入多个分区（使用分区表和擦除）
fastboot flashall -w -s
# 刷入多个分区（使用分区表和擦除用户数据）
fastboot flashall -w -u
# 刷入多个分区（使用分区表和擦除缓存）
fastboot flashall -w -c
```

## Fastboot 源码

Fastboot 的源码通常可以在 Android Open Source Project (AOSP) 中找到。以下是一些常见的 Fastboot 源码文件和目录：

- `fastboot/`: Fastboot 的主要源代码目录，包含 Fastboot 命令的实现。
- `fastboot/commands/`: 包含 Fastboot 命令的实现文件。
- `fastboot/transport/`: 包含与设备通信的传输层实现。
- `fastboot/usb/`: 包含 USB 相关的实现文件。
- `fastboot/fastboot.cpp`: Fastboot 的主入口文件，包含 Fastboot 命令的解析和执行逻辑。
- `fastboot/fastboot.h`: Fastboot 的头文件，定义了 Fastboot 命令和数据结构。
- `fastboot/fastboot_commands.cpp`: 包含 Fastboot 命令的具体实现，如刷入镜像、解锁引导加载程序等。
- `fastboot/fastboot_transport.cpp`: 包含与设备通信的传输层实现，如 USB 通信。
- `fastboot/fastboot_usb.cpp`: 包含 USB 相关的实现文件，如 USB 设备的识别和通信。
- `fastboot/fastboot_utils.cpp`: 包含一些实用函数，如日志记录、错误处理等。
- `fastboot/fastboot_config.cpp`: 包含 Fastboot 配置的实现，如命令行参数解析等。
- `fastboot/fastboot_commands.h`: Fastboot 命令的头文件，定义了 Fastboot 命令的接口和数据结构。
- `fastboot/fastboot_transport.h`: Fastboot 传输层的头文件，定义了与设备通信的接口和数据结构。
- `fastboot/fastboot_usb.h`: Fastboot USB 相关的头文件，定义了 USB 设备的接口和数据结构。
- `fastboot/fastboot_utils.h`: Fastboot 实用函数的头文件，定义了一些常用的函数和数据结构。
- `fastboot/fastboot_config.h`: Fastboot 配置的头文件，定义了 Fastboot 命令行参数的解析和配置。

## Fastboot 设备端源码分析

Fastboot 设备端（即运行在 Android 设备上的 bootloader 部分）源码主要实现了 Fastboot 协议的解析、命令处理、分区操作和 USB 通信等功能。下面结合 AOSP 常见目录结构和关键源码文件，详细解析 Fastboot 设备端的实现原理。

---

### 1. Fastboot 设备端源码主要目录

- `bootable/bootloader/`  
  设备端 bootloader 相关代码，常见实现有 U-Boot、LittleKernel（LK）、Aboot 等。
- `bootable/bootloader/lk/app/fastboot/`  
  LK 下 Fastboot 协议和命令处理实现。
- `bootable/bootloader/lk/platform/xxx/usb/`  
  平台相关的 USB 控制器驱动。
- `system/core/fastbootd/`  
  部分新设备支持 fastbootd，运行于 recovery 分区。

---

### 2. Fastboot 设备端核心模块

#### 2.1 USB 通信层

- **作用**：负责与 PC 端 fastboot 工具通过 USB 进行数据收发。
- **关键文件**：如 `usb.c`、`usb_device.c`、`usb_fastboot.c`
- **主要流程**：
  1. 初始化 USB 控制器，配置为设备模式。
  2. 注册 Fastboot 端点（通常为 Bulk IN/OUT）。
  3. 监听主机命令，收发数据包。

#### 2.2 Fastboot 协议解析与命令分发

- **作用**：解析主机发送的 Fastboot 命令字符串，分发到对应的处理函数。
- **关键文件**：如 `fastboot.c`、`fastboot_command.c`
- **主要流程**：
  1. 接收命令字符串（如 `flash:boot`、`getvar:version`）。
  2. 匹配命令前缀，调用注册的命令处理回调。
  3. 处理结果通过 USB 发送响应（如 `OKAY`、`FAIL`、`DATA`）。

#### 2.3 分区/存储操作

- **作用**：实现 flash、erase、read、write 等分区操作。
- **关键文件**：如 `flash.c`、`partition.c`
- **主要流程**：
  1. 解析分区名，查找分区表。
  2. 调用底层存储驱动（如 eMMC、UFS）进行实际数据操作。
  3. 返回操作结果。

#### 2.4 典型命令处理流程

以 `fastboot flash boot boot.img` 为例：

1. **主机发送命令**：`flash:boot`
2. **设备端解析命令**，找到 `flash` 处理函数。
3. **设备端等待主机发送数据**（`download` 阶段）。
4. **接收数据并写入指定分区**（如 boot）。
5. **发送 `OKAY` 或 `FAIL` 响应给主机**。

---

### 3. 关键结构体与函数

#### 3.1 命令注册与分发

```c
// 伪代码示例
struct fastboot_cmd {
    const char *prefix;
    void (*handler)(const char *arg, void *data, unsigned sz);
};

void fastboot_register(const char *prefix, void (*handler)(...)) {
    // 注册命令及其处理函数
}

void fastboot_command_loop() {
    while (1) {
        char cmd[64];
        usb_read(cmd, sizeof(cmd));
        // 查找匹配的命令并调用 handler
    }
}
```

#### 3.2 数据收发

```c
// 接收主机数据
void fastboot_download(const char *arg, void *data, unsigned sz) {
    usb_read(data, sz);
    // 写入分区或缓存
}

// 发送响应
void fastboot_okay(const char *msg) {
    usb_write("OKAY", 4);
    usb_write(msg, strlen(msg));
}
```

---

### 4. 设备端常见命令实现

- `getvar`：查询设备信息（如版本、分区表等）。
- `flash`：刷写分区镜像。
- `erase`：擦除分区。
- `reboot`：重启设备。
- `oem`：厂商自定义命令。

---

### 5. 参考流程图

```plaintext
[USB初始化] → [命令接收] → [命令解析] → [命令处理] → [分区/存储操作] → [响应主机]
```
