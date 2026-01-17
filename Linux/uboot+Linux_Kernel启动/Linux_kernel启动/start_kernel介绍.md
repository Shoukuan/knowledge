# start_kernel介绍
<!-- TOC -->


<!-- TOC END -->


[start_kernel介绍](https://www.cnblogs.com/lifexy/p/7366782.html)

```C
asmlinkage void __init start_kernel(void) 

{ 
  char * command_line; 
  extern struct kernel_param __start___param[], __stop___param[];  

  smp_setup_processor_id();  //来设置smp process id，当然目前看到的代码里面这里是空的
  
  unwind_init(); 

//lockdep是linux内核的一个调试模块，用来检查内核互斥机制尤其是自旋锁潜在的死锁问题。  
//自旋锁由于是查询方式等待，不释放处理器，比一般的互斥机制更容易死锁，  
//故引入lockdep检查以下几种情况可能的死锁（lockdep将有专门的文章详细介绍，在此只是简单列举）：  
//  
//·同一个进程递归地加锁同一把锁；  
//  
//·一把锁既在中断（或中断下半部）使能的情况下执行过加锁操作，  
// 又在中断（或中断下半部）里执行过加锁操作。这样该锁有可能在锁定时由于中断发生又试图在同一处理器上加锁；  
//  
//·加锁后导致依赖图产生成闭环，这是典型的死锁现象。  
   lockdep_init(); 
   

//关闭当前CUP中断  
local_irq_disable(); 

//修改标记early_boot_irqs_enabled;  
//通过一个静态全局变量 early_boot_irqs_enabled来帮助我们调试代码，  
//通过这个标记可以帮助我们知道是否在”early bootup code”，也可以通过这个标志警告是有无效的终端打开  
early_boot_irqs_off(); 

//每一个中断都有一个IRQ描述符（struct irq_desc）来进行描述。  
//这个函数的主要作用是设置所有的 IRQ描述符（struct irq_desc）的锁是统一的锁，  
//还是每一个IRQ描述符（struct irq_desc）都有一个小锁。  
early_init_irq_lock_class(); 


/*

 * Interrupts are still disabled. Do necessary setups, then
 * enable them
 */ 
// 大内核锁（BKL--Big Kernel Lock）  
//大内核锁本质上也是自旋锁，但是它又不同于自旋锁，自旋锁是不可以递归获得锁的，因为那样会导致死锁。  
//但大内核锁可以递归获得锁。大内核锁用于保护整个内核，而自旋锁用于保护非常特定的某一共享资源。  
//进程保持大内核锁时可以发生调度，具体实现是：  
//在执行schedule时，schedule将检查进程是否拥有大内核锁，如果有，它将被释放，以致于其它的进程能够获得该锁，  
//而当轮到该进程运行时，再让它重新获得大内核锁。注意在保持自旋锁期间是不运行发生调度的。  
//需要特别指出，整个内核只有一个大内核锁，其实不难理解，内核只有一个，而大内核锁是保护整个内核的，当然有且只有一个就足够了。  
//还需要特别指出的是，大内核锁是历史遗留，内核中用的非常少，一般保持该锁的时间较长，因此不提倡使用它。  
//从2.6.11内核起，大内核锁可以通过配置内核使其变得可抢占（自旋锁是不可抢占的），这时它实质上是一个互斥锁，使用信号量实现。  
//大内核锁的API包括：  
//  
//void lock_kernel(void);  
//  
//该函数用于得到大内核锁。它可以递归调用而不会导致死锁。  
//  
//void unlock_kernel(void);  
//  
//该函数用于释放大内核锁。当然必须与lock_kernel配对使用，调用了多少次lock_kernel，就需要调用多少次unlock_kernel。  
//大内核锁的API使用非常简单，按照以下方式使用就可以了：  
//lock_kernel(); //对被保护的共享资源的访问 … unlock_kernel()；  
//http://blog.csdn.net/universus/archive/2010/05/25/5623971.aspx  
  lock_kernel(); 


//初始化time ticket，时钟  
  tick_init(); 

 
//函数 tick_init() 很简单，调用 clockevents_register_notifier 函数向 clockevents_chain 通知链注册元素：  
// tick_notifier。这个元素的回调函数指明了当时钟事件设备信息发生变化（例如新加入一个时钟事件设备等等）时，  
//应该执行的操作，该回调函数为 tick_notify   
//http://blogold.chinaunix.net/u3/97642/showart_2050200.html  
  boot_cpu_init();


//初始化页地址，当然对于arm这里是个空函数  
//http://book.chinaunix.net/special/ebook/PrenticeHall/PrenticeHallPTRTheLinuxKernelPrimer/0131181637/ch08lev1sec5.html  
  page_address_init(); 


/*打印KER_NOTICE,这里的KER_NOTICE是字符串<5>*/
  printk(KERN_NOTICE);

 
 
/*打印以下linux版本信息:       
“Linux version 2.6.22.6 (book@book-desktop) (gcc version 3.4.5) #1 Fri Jun 16 00:55:53 CST 2017” */
 printk(linux_banner);
      

//系结构相关的内核初始化过程,处理uboot传递进来的atag参数( setup_memory_tags()和setup_commandline _tags() )  
//http://www.cublog.cn/u3/94690/showart_2238008.html  
setup_arch(&command_line); 

  

//处理启动命令，这里就是设置的cmd_line，
//保存未改变的comand_line到字符数组static_command_line［］ 中。
//保存  boot_command_line到字符数组saved_command_line［］中  
setup_command_line(command_line); 

unwind_setup();

//如果没有定义CONFIG_SMP宏，则这个函数为空函数。  
//如果定义了CONFIG_SMP宏，则这个setup_per_cpu_areas()函数给每个CPU分配内存，  
//并拷贝.data.percpu段的数据。为系统中的每个CPU的per_cpu变量申请空间。  
setup_per_cpu_areas();

//定义在include/asm-x86/smp.h。  
//如果是SMP环境，则设置boot CPU的一些数据。在引导过程中使用的CPU称为boot CPU  
smp_prepare_boot_cpu(); /* arch-specific boot-cpu hooks */ 
/* 进程调度器初始化 */
sched_init(); 

/* 禁止内核抢占 */  
preempt_disable();
      
//设置node 和 zone 数据结构  
//内存管理的讲解：http://blog.chinaunix.net/space.php?uid=361890&do=blog&cuid=2146541  
build_all_zonelists(NULL); 
 
//初始化page allocation相关结构  
page_alloc_init();

/* 打印Linux启动命令行参数 */   
printk(KERN_NOTICE "Kernel command line: %s/n", boot_command_line); 
  
//解析内核参数  
//对内核参数的解析：http://hi.baidu.com/yuhuntero/blog/item/654a7411e45ce519b8127ba9.html  
parse_early_param(); 
parse_args("Booting kernel", static_command_line, __start___param, 
  __stop___param - __start___param, 
  &unknown_bootoption); 

/*
* These use large bootmem allocations and must precede
* kmem_cache_init()
*/ 
//初始化hash表，以便于从进程的PID获得对应的进程描述指针，按照实际的物理内存初始化pid hash表  
//这里涉及到进程管理http://blog.csdn.net/satanwxd/archive/2010/03/27/5422053.aspx  
pidhash_init(); 

//初始化VFS的两个重要数据结构dcache和inode的缓存。  
//http://blog.csdn.net/yunsongice/archive/2011/02/01/6171324.aspx  
vfs_caches_init_early(); 

//把编译期间，kbuild设置的异常表，也就是__start___ex_table和__stop___ex_table之中的所有元素进行排序  
sort_main_extable(); 

//初始化中断向量表  
//http://blog.csdn.net/yunsongice/archive/2011/02/01/6171325.aspx  
trap_init(); 

//memory map初始化  
//http://blog.csdn.net/huyugv_830913/archive/2010/09/15/5886970.aspx  
mm_init(); 

/*
* Set up the scheduler prior starting any interrupts (such as the
* timer interrupt). Full topology setup happens at smp_init()
* time - but meanwhile we still have a functioning scheduler.
*/ 
//核心进程调度器初始化，调度器的初始化的优先级要高于任何中断的建立，  
//并且初始化进程0，即idle进程，但是并没有设置idle进程的NEED_RESCHED标志，  
//所以还会继续完成内核初始化剩下的事情。  
//这里仅仅为进程调度程序的执行做准备。  
//它所做的具体工作是调用init_bh函数(kernel/softirq.c)把timer,tqueue,immediate三个人物队列加入下半部分的数组  
sched_init(); 

/*
* Disable preemption - early bootup scheduling is extremely
* fragile until we cpu_idle() for the first time.
*/ 
//抢占计数器加1   
 preempt_disable();

 

//检查中断是否打开,如果已经打开，则关闭中断   
  if (!irqs_disabled()) { 
  printk(KERN_WARNING "start_kernel(): bug: interrupts were " 
  "enabled *very* early, fixing it/n"); 
  local_irq_disable(); 
  } 

 

  sort_main_extable();  /*
 * trap_init函数完成对系统保留中断向量（异常、非屏蔽中断以及系统调用）              
 * 的初始化，init_IRQ函数则完成其余中断向量的初始化
 */
 trap_init();    

//Read-Copy-Update的初始化  
//RCU机制是Linux2.6之后提供的一种数据一致性访问的机制，  
//从RCU（read-copy-update）的名称上看，我们就能对他的实现机制有一个大概的了解，  
//在修改数据的时候，首先需要读取数据，然后生成一个副本，对副本进行修改，  
//修改完成之后再将老数据update成新的数据，此所谓RCU。  
//http://blog.ednchina.com/tiloog/193361/message.aspx  
//http://blogold.chinaunix.net/u1/51562/showart_1341707.html  
rcu_init();
 
//初始化IRQ中断和终端描述符。  
//初始化系统中支持的最大可能的中断描述结构struct irqdesc变量数组irq_desc[NR_IRQS],  
//把每个结构变量irq_desc[n]都初始化为预先定义好的坏中断描述结构变量bad_irq_desc,  
//并初始化该中断的链表表头成员结构变量pend  
init_IRQ();    

/* 初始化hash表，便于从进程的PID获得对应的进程描述符指针 */
pidhash_init();

 

//初始化定时器Timer相关的数据结构  
//http://www.ibm.com/developerworks/cn/linux/l-cn-clocks/index.html  
init_timers();  

//对高精度时钟进行初始化  
hrtimers_init();
 
//软中断初始化  
//http://blogold.chinaunix.net/u1/51562/showart_494363.html  
softirq_init(); 
 
//初始化时钟源  
timekeeping_init(); 
 
//初始化系统时间，  
//检查系统定时器描述结构struct sys_timer全局变量system_timer是否为空，  
//如果为空将其指向dummy_gettimeoffset()函数。  
//http://www.ibm.com/developerworks/cn/linux/l-cn-clocks/index.html  
time_init();  

//profile只是内核的一个调试性能的工具，  
//这个可以通过menuconfig中的Instrumentation Support->profile打开。  
//http://www.linuxdiyf.com/bbs//thread-71446-1-1.html  
profile_init();
    
/*if判断中断是否打开,如果已经打开，打印数据*/   
if (!irqs_disabled()) 
    printk(KERN_CRIT "start_kernel(): bug: interrupts were enabled early/n"); 

//与开始的early_boot_irqs_off相对应  
early_boot_irqs_on(); 
 
//与local_irq_disbale相对应，开CPU中断  
local_irq_enable();

/** HACK ALERT! This is early. We're enabling the console before
* we've done PCI setups etc, and console_init() must be aware of
* this. But we do want output early, in case something goes wrong.
*/ 
//初始化控制台以显示printk的内容，在此之前调用的printk，只是把数据存到缓冲区里，  
//只有在这个函数调用后，才会在控制台打印出内容  
//该函数执行后可调用printk()函数将log_buf中符合打印级别要求的系统信息打印到控制台上。  
console_init(); 

if (panic_later) 
panic(panic_later, panic_param);  

//如果定义了CONFIG_LOCKDEP宏，那么就打印锁依赖信息，否则什么也不做  
lockdep_info(); 

/*
* Need to run this when irqs are enabled, because it wants
* to self-test [hard/soft]-irqs on/off lock inversion bugs
* too:
*/ 
//如果定义CONFIG_DEBUG_LOCKING_API_SELFTESTS宏  
//则locking_selftest()是一个空函数，否则执行锁自测  
 locking_selftest(); 

  

# ifdef CONFIG_BLK_DEV_INITRD
if (initrd_start && !initrd_below_start_ok && 
   page_to_pfn(virt_to_page((void *)initrd_start)) < min_low_pfn) { 
printk(KERN_CRIT "initrd overwritten (0x%08lx < 0x%08lx) - " 
   "disabling it./n",    page_to_pfn(virt_to_page((void *)initrd_start)), 
   min_low_pfn); 
initrd_start = 0; 
} 
# endif

 
 /* 虚拟文件系统的初始化 */
 vfs_caches_init_early();       
 cpuset_init_early();
 mem_init();

/* slab初始化 */
kmem_cache_init();  

//是否是对SMP的支持，单核是否需要？？这个要分析  
setup_per_cpu_pageset(); 

numa_policy_init(); 

if (late_time_init) 
   late_time_init(); 

//calibrate_delay（）函数可以计算出cpu在一秒钟内执行了多少次一个极短的循环，  
//计算出来的值经过处理后得到BogoMIPS 值，  
//Bogo是Bogus(伪)的意思，MIPS是millions of instructions per second(百万条指令每秒)的缩写。  
//这样我们就知道了其实这个函数是linux内核中一个cpu性能测试函数。  
//http://blogold.chinaunix.net/u2/86768/showart_2196664.html  
calibrate_delay();
   
//PID是process id的缩写  
//http://blog.csdn.net/satanwxd/archive/2010/03/27/5422053.aspx  
pidmap_init();

 /* 接下来的函数中，大多数都是为有关的管理机制建立专用的slab缓存 */ 
pgtable_cache_init();
 
/* 初始化优先级树index_bits_to_maxindex数组 */
prio_tree_init();          

//来自mm/rmap.c  
//分配一个anon_vma_cachep作为anon_vma的slab缓存。  
//这个技术是PFRA（页框回收算法）技术中的组成部分。  
//这个技术为定位而生——快速的定位指向同一页框的所有页表项。  
anon_vma_init();

    
# ifdef CONFIG_X86
if (efi_enabled) 
efi_enter_virtual_mode(); 
# endif

//根据物理内存大小计算允许创建进程的数量  
//http://www.jollen.org/blog/2006/11/jollen_linux_3_fork_init.html  
fork_init(totalram_pages);

   
//给进程的各种资源管理结构分配了相应的对象缓存区  
//http://www.shangshuwu.cn/index.php/Linux内核的进程创建  
proc_caches_init(); 

//创建 buffer_head SLAB 缓存  
buffer_init(); 

unnamed_dev_init();

//初始化key的management stuff  
key_init(); 

//关于系统安全的初始化，主要是访问控制  
//http://blog.csdn.net/nhczp/archive/2008/04/29/2341194.aspx  
security_init();  

//调用kmem_cache_create()函数来为VFS创建各种SLAB分配器缓存  
//包括：names_cachep、filp_cachep、dquot_cachep和bh_cachep等四个SLAB分配器缓存  
vfs_caches_init(totalram_pages); 
 
radix_tree_init(); 

//创建信号队列  
signals_init();

   

/* rootfs populating might need page-writeback */ 
//回写相关的初始化  
//http://blog.csdn.net/yangp01/archive/2010/04/06/5454822.aspx  \page_writeback_init();   

# ifdef CONFIG_PROC_FS
   proc_root_init(); 
# endif

//http://blogold.chinaunix.net/u1/51562/showart_1777937.html  
cpuset_init();
 
////进程状态初始化，实际上就是分配了一个存储线程状态的高速缓存  
taskstats_init_early(); 

delayacct_init();  

//测试CPU的各种缺陷，记录检测到的缺陷，以便于内核的其他部分以后可以使用他们工作。  
check_bugs(); 
 
//电源相关的初始化  
//http://blogold.chinaunix.net/u/548/showart.php?id=377952  
acpi_early_init(); /* before LAPIC and SMP init */ 
 

//接着进入rest_init()创建init进程,创建根文件系统，启动应用程序
rest_init(); 
}
```

