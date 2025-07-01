# Linux PCIe源码解析

在Linux内核中，PCIe驱动的实现主要涉及以下几个核心部分：PCIe设备的枚举、驱动注册、设备探测、资源管理、数据传输和中断处理等。下面将详细解析Linux PCIe驱动的源码实现。

---

## 0. 源码目录结构

Linux内核中与PCIe相关的源码主要位于以下目录：

drivers/pci/：PCI/PCIe核心驱动代码。  
pci.c：PCI/PCIe核心功能的实现。  
pcie/：PCIe特定功能的实现。  
host/：PCIe主机控制器驱动。  
controller/：PCIe控制器驱动。  
access.c：PCI配置空间访问的实现。  
quirks.c：处理特定硬件的问题（quirks）。  
include/linux/pci.h：PCI/PCIe相关的头文件。  
Documentation/PCI/：PCI/PCIe相关的文档  

**核心功能模块**  
**设备枚举**  
pci_scan_bus()：扫描总线上的设备。  
pci_scan_slot()：扫描特定插槽上的设备。  
pci_scan_single_device()：扫描单个设备。  
**驱动注册**  
pci_register_driver()：注册PCI驱动。  
pci_unregister_driver()：注销PCI驱动。  
**资源管理**  
pci_request_regions()：请求设备资源。  
pci_iomap()：映射BAR到内核地址空间。  
pci_release_regions()：释放设备资源。  
**中断处理**  
pci_enable_msi()：启用MSI中断。  
pci_enable_msix()：启用MSI-X中断。  
request_irq()：注册中断处理函数。  
**数据传输**  
ioread32() / iowrite32()：读写MMIO寄存器。  
dma_alloc_coherent()：分配DMA缓冲区。  

---

## 1. **PCIe驱动的基本结构**

PCIe驱动的核心是 `struct pci_driver`，它定义了驱动的名称、设备ID表、探测函数、移除函数等。

```c
#include <linux/pci.h>

static const struct pci_device_id my_pci_tbl[] = {
    { PCI_DEVICE(VENDOR_ID, DEVICE_ID) }, // 设备ID表
    { 0, }
};
MODULE_DEVICE_TABLE(pci, my_pci_tbl);

static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id) {
    // 设备探测函数
    return 0;
}

static void my_pci_remove(struct pci_dev *pdev) {
    // 设备移除函数
}

static struct pci_driver my_pci_driver = {
    .name = "my_pci_driver",
    .id_table = my_pci_tbl, // 设备ID表
    .probe = my_pci_probe,  // 探测函数
    .remove = my_pci_remove, // 移除函数
};

module_pci_driver(my_pci_driver); // 注册驱动
```

---

## 2. **设备探测（Probe）**

在设备探测函数中，驱动需要完成以下任务：

- 启用设备：`pci_enable_device()`
- 请求资源：`pci_request_regions()`
- 映射BAR：`pci_iomap()`
- 初始化设备（如配置寄存器、设置中断等）

```c
static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id) {
    int ret;
    void __iomem *bar;

    // 启用设备
    ret = pci_enable_device(pdev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to enable PCI device\n");
        return ret;
    }

    // 请求资源
    ret = pci_request_regions(pdev, "my_pci_driver");
    if (ret) {
        dev_err(&pdev->dev, "Failed to request PCI regions\n");
        goto disable_device;
    }

    // 映射BAR0
    bar = pci_iomap(pdev, 0, 0);
    if (!bar) {
        dev_err(&pdev->dev, "Failed to map BAR0\n");
        ret = -ENOMEM;
        goto release_regions;
    }

    // 初始化设备（例如配置寄存器）
    iowrite32(0x12345678, bar + REG_OFFSET);

    // 设置中断
    ret = pci_enable_msi(pdev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to enable MSI\n");
        goto unmap_bar;
    }
    ret = request_irq(pdev->irq, my_interrupt_handler, 0, "my_pci_driver", pdev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to request IRQ\n");
        goto disable_msi;
    }

    // 保存设备私有数据
    pci_set_drvdata(pdev, bar);

    return 0;

disable_msi:
    pci_disable_msi(pdev);
unmap_bar:
    pci_iounmap(pdev, bar);
release_regions:
    pci_release_regions(pdev);
disable_device:
    pci_disable_device(pdev);
    return ret;
}
```

---

## 3. **设备移除（Remove）**

在设备移除函数中，驱动需要释放所有分配的资源：

- 释放中断：`free_irq()`
- 取消映射BAR：`pci_iounmap()`
- 释放资源：`pci_release_regions()`
- 禁用设备：`pci_disable_device()`

```c
static void my_pci_remove(struct pci_dev *pdev) {
    void __iomem *bar = pci_get_drvdata(pdev);

    // 释放中断
    free_irq(pdev->irq, pdev);
    pci_disable_msi(pdev);

    // 取消映射BAR
    pci_iounmap(pdev, bar);

    // 释放资源
    pci_release_regions(pdev);

    // 禁用设备
    pci_disable_device(pdev);
}
```

---

## 4. **中断处理**

中断处理函数用于处理设备触发的中断。在Linux中，中断处理函数需要快速完成，通常通过任务队列或工作队列将复杂任务推迟到中断上下文之外。

```c
static irqreturn_t my_interrupt_handler(int irq, void *dev_id) {
    struct pci_dev *pdev = dev_id;
    void __iomem *bar = pci_get_drvdata(pdev);

    // 读取中断状态
    u32 status = ioread32(bar + STATUS_REG);
    if (!(status & INT_STATUS_MASK)) {
        return IRQ_NONE; // 不是本设备的中断
    }

    // 处理中断
    // ...

    // 清除中断标志
    iowrite32(status, bar + STATUS_REG);

    return IRQ_HANDLED;
}
```

---

## 5. **数据传输**

PCIe驱动通常通过MMIO（Memory-Mapped I/O）或DMA（Direct Memory Access）进行数据传输。

### **MMIO**

```c
// 写寄存器
iowrite32(value, bar + REG_OFFSET);

// 读寄存器
u32 value = ioread32(bar + REG_OFFSET);
```

### **DMA**

```c
// 分配DMA缓冲区
dma_addr_t dma_handle;
void *buffer = dma_alloc_coherent(&pdev->dev, size, &dma_handle, GFP_KERNEL);

// 启动DMA传输
iowrite32(dma_handle, bar + DMA_ADDR_REG);
iowrite32(size, bar + DMA_SIZE_REG);
iowrite32(DMA_START, bar + DMA_CTRL_REG);

// 释放DMA缓冲区
dma_free_coherent(&pdev->dev, size, buffer, dma_handle);
```

---

## 6. **内核源码中的PCIe驱动示例**

Linux内核源码中有许多PCIe驱动的实现，可以参考以下目录：

- `drivers/pci/`：PCIe核心代码。
- `drivers/net/ethernet/`：网卡驱动（如Intel e1000e）。
- `drivers/gpu/drm/`：显卡驱动（如NVIDIA、AMD）。

---

## 7. **调试和测试**

- 使用 `dmesg` 查看内核日志。
- 使用 `lspci -vvv` 查看PCIe设备的详细信息。
- 使用 `cat /proc/interrupts` 查看中断信息。

---
