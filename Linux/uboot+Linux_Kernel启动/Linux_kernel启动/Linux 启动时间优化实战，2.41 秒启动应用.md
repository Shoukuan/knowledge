# Linux 启动时间优化实战，2.41 秒启动应用
<!-- TOC -->

- [1. 上电和引导加载程序（Uboot启动阶段）](#1-uboot)
- [2. 内核引导阶段（Kernel启动阶段）](#2-kernel)
- [3. 内核解压和初始化](#3-)
  - [解压内核](#)
    - [early_initcall 系列初始化](#early_initcall-)
    - [架构相关的初始化](#)
    - [内存管理初始化](#)
    - [命令行参数解析](#)
    - [陷阱初始化](#)
    - [RCU 和调度器初始化](#rcu-)
    - [时间管理初始化](#)
    - [控制台初始化](#)
    - [系统控制台初始化](#)
    - [中断初始化](#)
    - [定时器初始化](#)
    - [内核子系统初始化](#)
    - [创建内核线程](#)
  - [基本设置](#)
- [4. 启动内核线程](#4-)
- [5. 内核初始化阶段](#5-)
- [6. 启动用户空间的 init 进程](#6--init-)
- [7. init 进程和用户空间](#7-init-)

<!-- TOC END -->


[Linux 启动时间优化实战，2.41 秒启动应用！](https://cloud.tencent.com/developer/article/1991012)

Linux 内核启动过程是一个复杂且多步骤的过程，从系统上电开始，到最终启动用户空间的 init 进程。这个过程涉及多层次的初始化和配置，以下是详细的启动过程，包括关键的函数调用：

## 1. 上电和引导加载程序（Uboot启动阶段）

上电：系统上电后，处理器从固件（如 BIOS 或 UEFI）开始执行。  
引导加载程序：BIOS/UEFI 会加载引导加载程序（如 GRUB）。引导加载程序负责将 Linux 内核加载到内存，并将控制权交给内核，源码在**start.s**中

## 2. 内核引导阶段（Kernel启动阶段）

进入内核：引导加载程序将内核映像加载到内存，并跳转到内核的入口点,直接修改PC寄存器的值为Linux内核所在的地址。  
启动汇编代码：内核的启动代码（通常是 **arch/x86/boot/header.S 和 arch/x86/boot/compressed/head.S**）开始执行。

## 3. 内核解压和初始化

### 解压内核

start_kernel()：这是内核解压后的入口点，位于 init/main.c 中。

#### early_initcall 系列初始化

set_task_stack_end_magic(&init_task)：设置初始任务的栈末端魔术值。  
smp_setup_processor_id()：设置处理器 ID（多处理器支持）。  
debug_objects_early_init()：早期调试对象初始化。  

#### 架构相关的初始化

boot_cpu_init()：初始化启动 CPU。  
page_address_init()：初始化页面地址。  
pr_notice("%s", linux_banner)：打印 Linux 内核标识。  
early_security_init()：早期安全初始化。  
setup_arch(&command_line)：设置架构相关的初始化，并解析内核命令行参数。  

#### 内存管理初始化

mm_init_cpumask(&init_mm)：初始化内存管理 CPU 掩码。  
setup_command_line(command_line)：设置命令行。  
setup_nr_cpu_ids()：设置 CPU 数量。  
setup_per_cpu_areas()：设置每 CPU 区域。  
smp_prepare_boot_cpu()：准备启动 CPU。  
build_all_zonelists(NULL, NULL)：构建所有区域列表。  
page_alloc_init()：页面分配初始化。  

#### 命令行参数解析

parse_early_param()：解析早期参数。  
jump_label_init()：初始化跳转标签。  
parse_args()：解析命令行参数。  

#### 陷阱初始化

trap_init()：陷阱初始化。  
mm_init()：内存管理初始化。  
ftrace_init()：函数追踪初始化。  

#### RCU 和调度器初始化

rcu_init()：初始化 RCU（Read-Copy-Update）子系统。  
preempt_disable()：禁用抢占。  
radix_tree_init()：基数树初始化。  
random_init()：随机数初始化。  
perf_event_init()：性能事件初始化。  
kmemleak_init()：内存泄漏检测初始化。  
sched_init()：调度器初始化。  

#### 时间管理初始化

timekeeping_init()：时间管理初始化。  
time_init()：时间初始化。  
softirq_init()：软中断初始化。  
tick_init()：时钟滴答初始化。  

#### 控制台初始化

console_init()：控制台初始化。  

#### 系统控制台初始化

初始化系统控制台，处理早期消息抑制。

#### 中断初始化

init_irq()：中断初始化。

#### 定时器初始化

init_timers()：定时器初始化。  
hrtimers_init()：高精度定时器初始化。  

#### 内核子系统初始化

pidmap_init()：PID 映射初始化。  
anon_vma_init()：匿名虚拟内存区域初始化。  
fork_init()：进程创建初始化。  
proc_caches_init()：进程缓存初始化。
buffer_init()：缓冲区初始化。  
key_init()：密钥管理初始化。  
security_init()：安全初始化。  
dbg_late_init()：调试初始化。  
vfs_caches_init_early()：虚拟文件系统缓存早期初始化。  
page_writeback_init()：页面写回初始化。  
mem_init()：内存初始化。  
kmem_cache_init()：内核内存缓存初始化。  
kmem_cache_init_late()：内核内存缓存后期初始化。  
usercopy_init()：用户拷贝初始化。  

#### 创建内核线程

rest_init()：创建初始内核线程（init 和 kthreadd），并进入 idle 循环。

### 基本设置

setup_arch(&command_line)：设置体系结构相关的初始化。

mm_init()：内存管理初始化。

sched_init()：调度器初始化。

rest_init()：剩余初始化，包括创建初始内核线程（pid 0），然后 pid 1 的 init 进程。

## 4. 启动内核线程

rest_init() 函数：创建内核线程。

```C
noinline void __ref rest_init(void)
{
    struct task_struct *tsk;
    int pid;

    rcu_scheduler_starting();
    /*
     * We need to spawn init first so that it obtains pid 1, however
     * the init task will end up wanting to create kthreads, which, if
     * we schedule it before we create kthreadd, will OOPS.
     */
    pid = kernel_thread(kernel_init, NULL, CLONE_FS);
    /*
     * Pin init on the boot CPU. Task migration is not properly working
     * until sched_init_smp() has been run. It will set the allowed
     * CPUs for init to the non isolated CPUs.
     */
    rcu_read_lock();
    tsk = find_task_by_pid_ns(pid, &init_pid_ns);
    set_cpus_allowed_ptr(tsk, cpumask_of(smp_processor_id()));
    rcu_read_unlock();

    numa_default_policy();
    pid = kernel_thread(kthreadd, NULL, CLONE_FS | CLONE_FILES);
    rcu_read_lock();
    kthreadd_task = find_task_by_pid_ns(pid, &init_pid_ns);
    rcu_read_unlock();

    /*
     * Enable might_sleep() and smp_processor_id() checks.
     * They cannot be enabled earlier because with CONFIG_PREEMPTION=y
     * kernel_thread() would trigger might_sleep() splats. With
     * CONFIG_PREEMPT_VOLUNTARY=y the init task might have scheduled
     * already, but it's stuck on the kthreadd_done completion.
     */
    system_state = SYSTEM_SCHEDULING;

    complete(&kthreadd_done);

    /*
     * The boot idle thread must execute schedule()
     * at least once to get things moving:
     */
    schedule_preempt_disabled();
    /* Call into cpu_idle with preempt disabled */
    cpu_startup_entry(CPUHP_ONLINE);
}
```

调用 rcu_scheduler_starting() 来通知 RCU 调度器已经启动。RCU（Read-Copy-Update）是内核中用于实现高效并发访问的一种机制。

kernel_thread(kernel_init, NULL, CLONE_FS | CLONE_SIGHAND)：创建初始内核线程。入口函数是kernel_init，kernel_init()：内核线程的主函数。
kernel_init 线程会成为用户空间的第一个进程，负责启动系统的其他部分。kthreadd 线程负责管理内核中的所有内核线程

## 5. 内核初始化阶段

内核子系统初始化：

do_basic_setup()：初始化核心子系统和设备。

do_initcalls()：执行内核模块的初始化函数。

挂载根文件系统：

prepare_namespace()：挂载根文件系统。

## 6. 启动用户空间的 init 进程

运行 init 进程：
run_init_process()：尝试运行用户空间的 init 进程（/sbin/init、/etc/init、/bin/init 等）。

## 7. init 进程和用户空间

用户空间的 init 进程：init 进程（PID 1）开始运行，它会启动其他系统服务和用户空间进程。
启动服务：init 进程根据初始化脚本或配置文件（如 systemd 或 SysVinit）启动各种系统服务和守护进程。
关键函数调用顺序概述
start_kernel()：内核的主要入口点。
setup_arch()：设置体系结构相关的初始化。
mm_init()：内存管理初始化。
sched_init()：调度器初始化。
rest_init()：剩余初始化，创建初始内核线程。
kernel_thread(kernel_init)：创建初始内核线程。
kernel_init()：内核线程的主函数，进一步初始化内核。
do_basic_setup()：初始化核心子系统和设备。
do_initcalls()：执行内核模块的初始化函数。
prepare_namespace()：挂载根文件系统。
run_init_process()：尝试运行用户空间的 init 进程。
整个过程确保了系统从上电到运行用户空间进程的完整启动，涵盖了内核的解压、初始化、核心子系统配置、设备初始化、文件系统挂载以及最终启动用户空间的 init 进程。

