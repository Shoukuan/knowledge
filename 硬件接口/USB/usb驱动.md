# 基于cherryUSB的USB驱动实现详解
<!-- TOC -->

- [1. 概述](#1-)
- [2. 驱动结构](#2-)
- [3. 实现流程](#3-)
  - [3.1 控制器初始化](#31-)
    - [3.1.1 初始化流程概览](#311-)
    - [3.1.2 关键代码与步骤说明](#312-)
  - [3.2. 设备枚举与配置流程](#32-)
    - [3.2.1 等待主机枚举](#321-)
    - [3.2.2 总线复位](#322-)
    - [3.2.3 主机请求设备描述符](#323-)
    - [3.2.4 分配设备地址](#324-)
    - [3.2.5 配置端点和加载类驱动](#325-)
  - [3.3 数据传输](#33-)
    - [3.3.1. 上层协议栈提交传输请求](#331-)
    - [3.3.2. HAL 层构建传输并启动](#332-hal-)
    - [3.3.3. 处理中断，检测传输完成或错误](#333-)
    - [3.3.4. 回调上层，通知结果并回收资源](#334-)
  - [3.4 中断处理](#34-)
    - [3.4.1 中断服务函数注册](#341-)
    - [3.4.2 中断服务函数（ISR）实现](#342-isr)
    - [3.4.3 总线复位（RESET）](#343-reset)
    - [3.4.4 控制端点0事件（EP0）](#344-0ep0)
    - [3.4.5 其他端点事件（EPn）](#345-epn)
  - [3.5 错误处理与恢复](#35-)
- [4. 关键数据结构](#4-)
- [5. 示例代码片段](#5-)
- [DWC3](#dwc3)
  - [1. 接收数据包（Receiving a Data Packet）寄存器操作流程](#1-receiving-a-data-packet)
    - [1.1 流程步骤](#11-)
  - [1.2 典型寄存器操作伪代码](#12-)
  - [2. 发送数据包（Transmitting a Data Packet）寄存器操作流程](#2-transmitting-a-data-packet)
    - [2.1 流程步骤](#21-)
    - [2.2 典型寄存器操作伪代码](#22-)
  - [3. 时序图示意](#3-)
    - [3.1 接收数据包（OUT传输）](#31-out)
    - [3.2 发送数据包（IN传输）](#32-in)

<!-- TOC END -->


## 1. 概述

cherryUSB 是一款开源、跨平台的 USB 协议栈，支持主机（Host）和设备（Device）模式，适用于多种 MCU/SoC 平台。其驱动实现以模块化、可移植为设计目标，便于适配不同硬件控制器。cherryUSB 驱动主要负责 USB 控制器的初始化、设备枚举、数据传输和中断处理等核心功能。
  
[cherryUSB GitHub 代码库](https://github.com/sakumisu/cherryusb)
  
## 2. 驱动结构

cherryUSB 驱动结构分为三层：

**硬件抽象层（HAL）**：针对不同芯片的 USB 控制器实现底层寄存器操作、端点配置和中断管理，提供统一接口。在硬件抽象层（HAL）中，主要涉及以下几个方面：

- **寄存器操作**：HAL 层需要直接操作 USB 控制器的寄存器，包括控制寄存器（如使能、复位、时钟配置）、端点寄存器（配置端点类型、方向、最大包长）、中断寄存器（使能/清除中断标志）、FIFO/DMA 寄存器（数据缓冲区管理）等。具体寄存器名称和位域依赖于芯片厂商的数据手册。

- **端点配置**：通过设置端点控制寄存器，指定端点号、类型（控制、批量、中断、同步）、方向（IN/OUT）、最大包长等参数。通常还需为每个端点分配缓冲区，并初始化端点状态（如空闲、忙、STALL）。

- **中断配置**：HAL 层负责使能 USB 控制器相关的中断（如总线复位、端点传输完成、错误、SOF 等），并在中断向量表中注册中断服务函数。中断服务函数需读取中断标志寄存器，分辨中断类型，并调用协议栈相应的事件处理接口。部分平台还需配置中断优先级和触发方式（边沿/电平）。

**核心协议栈层**：实现 USB 协议解析、设备/主机状态机、端点管理、数据调度等功能，屏蔽硬件差异。

- **协议解析**：解析 USB 标准请求（如 GET_DESCRIPTOR、SET_ADDRESS、SET_CONFIGURATION 等），并根据请求类型分发到对应处理函数。
- **状态机管理**：维护 USB 设备或主机的状态（如 Default、Address、Configured），根据协议流程切换状态。
- **端点管理**：统一管理所有端点（EP0~EPn），包括端点的配置、数据收发、状态切换（如 STALL、NAK）。
- **数据调度**：负责数据包的收发调度，协调 HAL 层的数据传输和上层类驱动的数据请求。
- **事件分发**：接收 HAL 层的中断事件（如复位、传输完成），并分发到协议栈内部或类驱动处理。

**类驱动层**：实现具体的 USB 设备类（如CDC、MSC、HID等）或主机类（如HUB、MSC等）协议。

## 3. 实现流程

### 3.1 控制器初始化

cherryUSB 的控制器初始化过程主要涉及 HAL 层和协议栈层的协作，确保 USB 控制器硬件和协议栈软件处于可用状态。下面结合典型代码和流程详细说明：

---

#### 3.1.1 初始化流程概览

1. **寄存器和时钟配置**（HAL 层）
2. **端点资源初始化**（协议栈层）
3. **中断服务函数注册**（HAL 层）
4. **协议栈和类驱动注册**（协议栈层）
5. **启动控制器，进入监听状态**

---

#### 3.1.2 关键代码与步骤说明

##### 3.1.2.1 HAL 层初始化

HAL 层负责底层硬件的初始化，通常包括时钟使能、复位、寄存器映射等。例如：

```c
void usb_hardware_init(void) {
    // 使能 USB 控制器时钟
    USB_CLK_ENABLE();
    // 复位 USB 控制器
    USB_RESET();
    // 配置必要的寄存器
    USB->CTRL = USB_CTRL_ENABLE;
    // ...其他硬件相关初始化
}
```

##### 3.1.2.2 端点资源初始化

协议栈层会初始化端点池，分配缓冲区，设置端点初始状态：

```c
void usbd_initialize(void) {
    memset(&usbd_core_driver, 0, sizeof(usbd_core_driver));
    usbd_core_driver.device_state = USB_DEFAULT;
    // 初始化端点池
    for (int i = 0; i < USB_MAX_ENDPOINTS; i++) {
        usbd_core_driver.ep_pool[i].status = EP_IDLE;
        // 分配缓冲区等
    }
    // 调用 HAL 层初始化
    usb_hardware_init();
    // 使能中断
    usb_enable_irq();
}
```

##### 3.1.2.3 注册中断服务函数

在 HAL 层注册 USB 中断服务函数，确保中断事件能被协议栈正确处理：

```c
void usb_enable_irq(void) {
    NVIC_SetPriority(USB_IRQn, 2);
    NVIC_EnableIRQ(USB_IRQn);
}
```

##### 3.1.2.4 协议栈和类驱动注册

注册 USB 描述符和类驱动，完成协议栈初始化：

```c
usbd_desc_register(dev_desc, cfg_desc, str_desc); // 注册描述符
usbd_class_register(&cdc_acm_class_driver);       // 注册类驱动
usbd_initialize();                               // 初始化协议栈
```

##### 3.1.2.5 启动控制器

最后，启动 USB 控制器，进入监听状态，等待主机枚举：

```c
void usb_start(void) {
    USB->CTRL |= USB_CTRL_START;
}
```

### 3.2. 设备枚举与配置流程

#### 3.2.1 等待主机枚举

   设备上电后，USB 控制器初始化并进入监听状态，等待主机发起枚举流程。

#### 3.2.2 总线复位

   主机检测到设备插入后，会对总线进行复位。此时协议栈会收到 RESET 中断，重置设备状态和端点。

   ```c
   // filepath: cherryusb/core/usbd_core.c
   void usbd_event_reset(void) {
       usbd_core_driver.device_state = USB_DEFAULT;
       memset(usbd_core_driver.ep_pool, 0, sizeof(usbd_core_driver.ep_pool));
       // 重新配置端点0
       hal_usb_ep_config(0, EP_TYPE_CONTROL, EP_DIR_OUT, EP0_MAX_PACKET_SIZE);
   }
   ```

#### 3.2.3 主机请求设备描述符

   主机通过控制端点（EP0）发送 GET_DESCRIPTOR 请求，协议栈解析 SETUP 包并返回设备描述符。

   ```c
   // filepath: cherryusb/core/usbd_core.c
   void usbd_event_ep0(void) {
       struct usb_setup_packet setup;
       usbd_read_setup_packet(&setup);
       usbd_setup_request_handler(&setup);
   }

   void usbd_setup_request_handler(struct usb_setup_packet *setup) {
       if (setup->bRequest == USB_REQUEST_GET_DESCRIPTOR) {
           // 查找并发送对应的描述符
           usbd_send_descriptor(setup);
       }
       // 其他标准请求处理
   }
   ```

#### 3.2.4 分配设备地址

   主机通过 SET_ADDRESS 请求分配设备地址，协议栈收到后设置内部地址状态。

   ```c
   void usbd_setup_request_handler(struct usb_setup_packet *setup) {
       if (setup->bRequest == USB_REQUEST_SET_ADDRESS) {
           usbd_core_driver.address = setup->wValue;
           // 等待状态阶段后由硬件设置地址
       }
   }
   ```

#### 3.2.5 配置端点和加载类驱动

   主机发送 SET_CONFIGURATION 请求，协议栈解析配置描述符，配置所有需要的端点，并初始化类驱动。

   ```c
   void usbd_setup_request_handler(struct usb_setup_packet *setup) {
       if (setup->bRequest == USB_REQUEST_SET_CONFIGURATION) {
           // 解析配置描述符，配置端点
           usbd_configure_endpoints();
           // 初始化并绑定类驱动
           if (usbd_core_driver.class_driver && usbd_core_driver.class_driver->init)
               usbd_core_driver.class_driver->init();
           usbd_core_driver.device_state = USB_CONFIGURED;
       }
   }
   ```

---

### 3.3 数据传输

cherryUSB 的数据传输流程分为上层请求、HAL 层执行、事件回调等几个环节，核心在于端点的数据收发调度和中断驱动。下面结合代码详细说明：

---

#### 3.3.1. 上层协议栈提交传输请求

上层（如类驱动）通过协议栈接口发起数据传输请求，常用函数有：

```c
int usbd_ep_start_write(uint8_t ep, const uint8_t *data, uint32_t len) {
    // 设置端点状态为忙
    usbd_core_driver.ep_pool[ep].status = EP_BUSY;
    // 调用 HAL 层接口启动写传输
    hal_usb_ep_write(ep, data, len);
    return 0;
}

int usbd_ep_start_read(uint8_t ep, uint8_t *data, uint32_t len) {
    usbd_core_driver.ep_pool[ep].status = EP_BUSY;
    hal_usb_ep_read(ep, data, len);
    return 0;
}
```

---

#### 3.3.2. HAL 层构建传输并启动

HAL 层负责具体的硬件操作，如配置 DMA/FIFO、启动传输等：

```c
void hal_usb_ep_write(uint8_t ep, const uint8_t *data, uint32_t len) {
    // 配置硬件 FIFO 或 DMA
    // 启动端点写传输
    USB->EP[ep].TXBUF = (uint32_t)data;
    USB->EP[ep].TXCNT = len;
    USB->EP[ep].CTRL |= USB_EP_TX_START;
}

void hal_usb_ep_read(uint8_t ep, uint8_t *data, uint32_t len) {
    // 配置硬件 FIFO 或 DMA
    USB->EP[ep].RXBUF = (uint32_t)data;
    USB->EP[ep].RXCNT = len;
    USB->EP[ep].CTRL |= USB_EP_RX_START;
}
```

---

#### 3.3.3. 处理中断，检测传输完成或错误

数据传输完成后，USB 控制器会产生中断，由中断服务函数统一处理：

```c
void USB_IRQHandler(void) {
    uint32_t int_flag = USB->INTFLAG;
    if (int_flag & USB_INT_EPn) {
        usbd_event_epn();
    }
    // ...其他中断处理
}
```

协议栈层根据端点号分发事件：

```c
void usbd_event_epn(void) {
    for (int ep = 1; ep < USB_MAX_ENDPOINTS; ep++) {
        if (/* 检查 ep 传输完成标志 */) {
            usbd_core_driver.ep_pool[ep].status = EP_IDLE;
            // 回调上层，通知数据传输完成
            if (usbd_core_driver.class_driver && usbd_core_driver.class_driver->ep_cb)
                usbd_core_driver.class_driver->ep_cb(ep, USBD_EVENT_TRANSFER_COMPLETE);
        }
    }
}
```

---

#### 3.3.4. 回调上层，通知结果并回收资源

传输完成后，协议栈会调用类驱动的回调函数，通知数据已收发完毕，类驱动可进行后续处理或再次提交请求。

### 3.4 中断处理

cherryUSB 的中断处理机制是驱动实现的核心之一，确保 USB 事件（如设备插拔、数据传输完成、错误等）能被及时响应和正确分发。下面结合源码详细说明其中断处理流程：

---

#### 3.4.1 中断服务函数注册

在 HAL 层初始化时，会注册 USB 控制器的中断服务函数（ISR），并设置优先级：

````c
void usb_enable_irq(void) {
    NVIC_SetPriority(USB_IRQn, 2);
    NVIC_EnableIRQ(USB_IRQn);
}
````

这样，当 USB 控制器产生中断时，系统会自动跳转到 `USB_IRQHandler`。

---

#### 3.4.2 中断服务函数（ISR）实现

中断服务函数通常在 HAL 层实现，负责读取中断标志寄存器，判断中断类型，并调用协议栈的事件处理接口：

````c
void USB_IRQHandler(void) {
    uint32_t int_flag = USB->INTFLAG;
    if (int_flag & USB_INT_RESET)
        usbd_event_reset();    // 处理总线复位
    if (int_flag & USB_INT_EP0)
        usbd_event_ep0();      // 处理控制端点0事件
    if (int_flag & USB_INT_EPn)
        usbd_event_epn();      // 处理其他端点事件
    // ...可扩展处理 SOF、SUSPEND 等
}
````

#### 3.4.3 总线复位（RESET）

收到 RESET 中断时，协议栈会重置设备状态和端点：

````c
void usbd_event_reset(void) {
    usbd_core_driver.device_state = USB_DEFAULT;
    memset(usbd_core_driver.ep_pool, 0, sizeof(usbd_core_driver.ep_pool));
    // 重新配置端点0
    hal_usb_ep_config(0, EP_TYPE_CONTROL, EP_DIR_OUT, EP0_MAX_PACKET_SIZE);
}
````

#### 3.4.4 控制端点0事件（EP0）

处理主机发来的 SETUP 包和标准请求：

````c
void usbd_event_ep0(void) {
    struct usb_setup_packet setup;
    usbd_read_setup_packet(&setup);
    usbd_setup_request_handler(&setup);
}
````

#### 3.4.5 其他端点事件（EPn）

检测端点传输完成，回调上层：

````c
void usbd_event_epn(void) {
    for (int ep = 1; ep < USB_MAX_ENDPOINTS; ep++) {
        if (/* 检查 ep 传输完成标志 */) {
            usbd_core_driver.ep_pool[ep].status = EP_IDLE;
            // 通知类驱动数据已完成
            if (usbd_core_driver.class_driver && usbd_core_driver.class_driver->ep_cb)
                usbd_core_driver.class_driver->ep_cb(ep, USBD_EVENT_TRANSFER_COMPLETE);
        }
    }
}
````

### 3.5 错误处理与恢复

- 检测传输超时、STALL、NAK 等错误
- 支持端点复位、控制器复位
- 重新提交失败的传输请求，保证数据可靠性

## 4. 关键数据结构

- `struct usbd_core_driver`：设备模式核心结构体，管理端点、缓冲区和状态机
- `struct usbh_core_driver`：主机模式核心结构体，管理设备列表、端口和传输队列
- `struct usb_endpoint`：端点描述，包含端点号、类型、缓冲区等信息
- `struct usb_setup_packet`：控制传输的 SETUP 包结构体
- `struct usbd_class_driver`：设备类驱动接口，定义类初始化、请求处理、数据回调等

## 5. 示例代码片段

```c
// 控制器初始化（设备模式）
usbd_desc_register(dev_desc, cfg_desc, str_desc);
usbd_class_register(&cdc_acm_class_driver);
usbd_initialize();

// 端点写数据
uint8_t data[] = "hello";
usbd_ep_start_write(CDC_IN_EP, data, sizeof(data));

// 中断处理（HAL 层伪代码）
void USB_IRQHandler(void) {
    uint32_t int_flag = USB->INTFLAG;
    if (int_flag & USB_INT_RESET)
        usbd_event_reset();
    if (int_flag & USB_INT_EP0)
        usbd_event_ep0();
    if (int_flag & USB_INT_EPn)
        usbd_event_epn();
}
```

## DWC3

好的，下面详细说明**Device模式下接收和发送数据包的寄存器操作流程**，并给出典型的时序图示意。

---

### 1. 接收数据包（Receiving a Data Packet）寄存器操作流程

#### 1.1 流程步骤

1. **端点配置**  
   软件通过端点配置寄存器（如 `ENDPOINTn_CONFIG`）设置端点类型、最大包长、方向（OUT）。

2. **使能端点**  
   设置端点使能位（如 `ENDPOINTn_ENABLE`），允许接收数据。

3. **等待中断**  
   控制器检测到主机OUT包，自动将数据写入端点接收FIFO，并在`INTR_OUT_EP`寄存器中置位对应端点的中断标志。

4. **中断响应**  
   CPU/固件检测到`INTR_OUT_EP`中断，读取`ENDPOINTn_OUT_FIFO`寄存器获取数据长度和内容。

5. **清除中断**  
   通过写`INTR_OUT_EP`寄存器清除中断标志。

### 1.2 典型寄存器操作伪代码

```c
// 1. 配置端点
ENDPOINT1_CONFIG = EP_TYPE_BULK | EP_DIR_OUT | EP_MAX_PKT_SIZE(512);
// 2. 使能端点
ENDPOINT1_ENABLE = 1;

// 3. 等待中断
while (!(INTR_OUT_EP & EP1_INT_FLAG));

// 4. 读取数据
uint32_t rx_len = ENDPOINT1_OUT_PKT_LEN;
for (int i = 0; i < rx_len; i++)
    buffer[i] = ENDPOINT1_OUT_FIFO;

// 5. 清除中断
INTR_OUT_EP = EP1_INT_FLAG;
```

---

### 2. 发送数据包（Transmitting a Data Packet）寄存器操作流程

#### 2.1 流程步骤

1. **端点配置**  
   配置端点为IN方向，设置类型和最大包长。

2. **写入数据**  
   将要发送的数据写入`ENDPOINTn_IN_FIFO`寄存器。

3. **设置数据长度**  
   写`ENDPOINTn_IN_PKT_LEN`寄存器，指定本次发送的数据长度。

4. **使能端点/启动传输**  
   设置`ENDPOINTn_ENABLE`或`ENDPOINTn_IN_START`寄存器，启动数据发送。

5. **等待中断**  
   控制器检测到主机IN令牌后自动发送数据，发送完成后在`INTR_IN_EP`寄存器中置位中断标志。

6. **清除中断**  
   写`INTR_IN_EP`寄存器清除中断。

#### 2.2 典型寄存器操作伪代码

```c
// 1. 配置端点
ENDPOINT1_CONFIG = EP_TYPE_BULK | EP_DIR_IN | EP_MAX_PKT_SIZE(512);
// 2. 写入数据
for (int i = 0; i < tx_len; i++)
    ENDPOINT1_IN_FIFO = buffer[i];
// 3. 设置数据长度
ENDPOINT1_IN_PKT_LEN = tx_len;
// 4. 启动传输
ENDPOINT1_ENABLE = 1;

// 5. 等待中断
while (!(INTR_IN_EP & EP1_INT_FLAG));

// 6. 清除中断
INTR_IN_EP = EP1_INT_FLAG;
```

---

### 3. 时序图示意

#### 3.1 接收数据包（OUT传输）

```plaintext
主机                控制器
 |  OUT Token  --->   |
 |  DATA Packet --->  |--[写入ENDPOINTn_OUT_FIFO]
 |                   |--[CRC校验]
 |                   |--[INTR_OUT_EP置位]
 |                   |--[CPU读取FIFO]
```

#### 3.2 发送数据包（IN传输）

```plaintext
主机                控制器
 |  IN Token   --->   |
 |                   |--[检测到IN Token]
 |                   |--[从ENDPOINTn_IN_FIFO取数据]
 |                   |--[发送DATA Packet]
 |                   |--[INTR_IN_EP置位]
 |                   |--[CPU清除中断]
```

---

