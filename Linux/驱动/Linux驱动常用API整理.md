---
title: Linux 驱动常用 API 整理
type: reference
status: active
tags: ["Linux", "驱动", "API", "字符设备", "中断", "设备树"]
aliases: ["Linux驱动API", "driver API reference"]
sources: ["https://nu-ll.github.io/2020/04/06/Linux驱动常用API整理/"]
updated_at: 2026-05-01
---
# Linux 驱动常用 API 整理

## 字符设备

```c
// 设备号
register_chrdev_region(dev_t from, count, name);   // 静态
alloc_chrdev_region(dev_t *dev, baseminor, count, name); // 动态

// cdev
cdev_init(cdev, fops);  cdev_add(cdev, dev, count);  cdev_del(cdev);
unregister_chrdev_region(from, count);

// 设备节点
class_create(owner, name);  class_destroy(cls);
device_create(cls, parent, devt, drvdata, fmt, ...);

// 数据拷贝
copy_to_user(to, from, n);  copy_from_user(to, from, n);
```

## 并发控制

| 机制 | 关键 API | 可休眠 |
|------|----------|--------|
| 原子操作 | `atomic_inc/dec/read`, `set_bit/clear_bit` | ❌ |
| 自旋锁 | `spin_lock/unlock`, `spin_lock_irqsave` | ❌ |
| 信号量 | `down/up`, `down_interruptible` | ✅ |
| 互斥体 | `mutex_lock/unlock`, `mutex_lock_interruptible` | ✅ |

中断只能用自旋锁，线程推荐互斥体。

## 中断

```c
request_irq(irq, handler, flags, name, dev);  free_irq(irq, dev);
enable_irq(irq);  disable_irq(irq);
local_irq_save(flags);  local_irq_restore(flags);

// 下半部 — tasklet（不能休眠）
DECLARE_TASKLET(name, func, data);  tasklet_schedule(&t);

// 下半部 — 工作队列（可休眠）
INIT_WORK(work, func);  schedule_work(work);
```

## 阻塞/非阻塞

```c
DECLARE_WAIT_QUEUE_HEAD(wq);
wait_event(wq, condition);  wait_event_interruptible(wq, condition);
wake_up(&wq);  wake_up_interruptible(&wq);

// 驱动 poll
poll_wait(filp, &wq, wait);
```

## IO 内存

```c
void __iomem *ioremap(phys_addr, size);  void iounmap(addr);
readb/readw/readl(addr);  writeb/writew/writel(value, addr);
```

## 定时器

```c
struct timer_list timer;
init_timer(&timer);  // .expires, .function, .data
add_timer(&timer);  mod_timer(&timer, expires);  del_timer(&timer);
// jiffies 转换: msecs_to_jiffies(), jiffies_to_msecs()
```

## Platform 驱动

```c
platform_driver_register(&drv);   // .probe, .remove, .driver.of_match_table
platform_driver_unregister(&drv);
```

## 设备树

```c
of_find_node_by_path(path);  of_get_parent(node);  of_get_next_child(node, prev);
of_property_read_u32(np, prop, &val);  of_property_read_string(np, prop, &str);
of_get_named_gpio(np, prop, index);  irq_of_parse_and_map(np, index);
```

## I2C / SPI

```c
// I2C
i2c_add_driver(&drv);  i2c_transfer(adap, msgs, num);
i2c_smbus_read_byte_data(client, cmd);

// SPI
spi_register_driver(&sdrv);  spi_sync(spi, &message);
spi_message_init(&m);  spi_message_add_tail(&t, &m);
```
