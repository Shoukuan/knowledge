---
title: Linux 字符设备驱动
type: note
status: active
tags: ["Linux", "驱动", "字符设备", "cdev", "file_operations"]
aliases: ["字符设备驱动", "char device driver", "cdev"]
sources: ["https://www.cnblogs.com/fortunely/p/16396800.html"]
updated_at: 2026-05-01
---
# Linux 字符设备驱动

字符设备按字节流顺序读写（键盘、串口、LED），每设备对应 `/dev` 下节点。

## 设备号 dev_t

32 位：高 12 主设备号 + 低 20 次设备号。`MAJOR/MINOR/MKDEV` 宏操作。

## cdev 结构体

```c
struct cdev { kobj, owner, *ops, dev, count; };
```

## 核心流程

```c
// 注册
alloc_chrdev_region(&dev, 0, 1, name);  // 或 register_chrdev_region
cdev_init(&cdev, &fops);
cdev.owner = THIS_MODULE;
cdev_add(&cdev, dev, 1);

// 注销
cdev_del(&cdev);
unregister_chrdev_region(dev, 1);
```

## file_operations

```c
struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = xxx_open, .release = xxx_release,
    .read = xxx_read, .write = xxx_write,
    .unlocked_ioctl = xxx_ioctl,
};
```

## 数据交换

```c
copy_to_user(to, from, n);    // 内核→用户
copy_from_user(to, from, n);  // 用户→内核
put_user / get_user            // 简单类型
```
返回值：未复制字节数，成功=0。

## 查看

```bash
cat /proc/devices   # 已注册字符设备
```

## 交叉链接

- [Linux 驱动常用 API](Linux驱动常用API整理.md)
