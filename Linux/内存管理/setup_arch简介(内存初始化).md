# setup_arch简介(内存管理初始化)

## start_kernel

`start_kernel`中和内存管理相关的系统初始化函数主要如下：

—->**setup_arch**: 体系机构的设置函数，还负责初始化自举分配器

—->setup_per_cpu_areas: 定义per-cpu变量,为各个cpu分别创建一份这些变量副本

—->build_all_zonelists: 建立节点(node)和内存域(zone)的数据结构

—->mem_init: 停用bootmem分配器并迁移到实际的内存管理函数

—->kmem_cache_init: 初始化内核内部用于小块内存区的分配器

—->setup_per_cpu_pageset: 为各个cpu的zone的pageset数组的第一个数组元素分配内存

## setup_arch

setup_arch

—->machine_specific_memory_setup: 创建一个列表，包括系统占据的内存区和空闲内存区

—->parse_early_param: 解析dtb树命令行

—->setup_memory: 确定每个节点可用的物理内存也数目，初始化bootmem分配器，分配各种内存区

—->paging_init: 初始化内核页表并启动内存分页

```php
---->pagetable_init: 确保直接映射到内核地址空间的物理内存被初始化
```

—->zone_size_init:初始化系统中所有节点的pgdat_t实例

```php
---->add_active_range: 对可用的物理内存建立一个相对简单的列表

---->free_area_init_nodes: 建立完备的内核数据结构
```
